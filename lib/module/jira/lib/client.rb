# frozen_string_literal: true

require 'cac/core/module/helpers'
require 'singleton'
require 'jira-ruby'
require 'io/console'
require 'keychain'

module CAC
  module Jira
    # The singleton Jira client
    class Client
      include Singleton
      include Cac::Core::Module::Helpers

      def client
        @client ||= configure_client
      end

      def getIssueTypeID(issuetype)
        issueID(issuetype)
      end

      private

      def issueID(issuetype)
        types = {
          'epic' => 20,
          'task' => 20_534,
          'crdb_cluster' => 21_686
        }
        types[issuetype]
      end

      def configure_client
        validate_config

        options = {
          username: config['username'],
          site: config['site'],
          context_path: config['context_path'],
          http_debug: false,
          auth_type: :basic
        }

        options[:password] = read_keychain_password(config[:username])

        JIRA::Client.new(options)
      end

      def validate_config
        logger.error "Please update cac.yaml with your site at YAML path 'cac/jira/site'" if config['project'] == 'https://jira.atlassian.com'
        logger.error "Please update cac.yaml with your project at YAML path 'cac/jira/project'" if config['project'] == 'INVALID_DEFAULT'
        logger.error "Please update cac.yaml with your username at YAML path 'cac/jira/username'" if config['username'] == 'INVALID_DEFAULT'
      end

      def read_keychain_password(username)
        keychain_item = Keychain.generic_passwords.where(service: 'cac-jira').first

        while keychain_item.nil?
          api_key = (print 'Jira API key: '
                     gets&.rstrip)
          Keychain.generic_passwords.create(service: 'cac-jira', password: api_key, account: username)
          keychain_item = Keychain.generic_passwords.where(service: 'cac-jira').first
        end

        keychain_item.password
      end
    end
  end
end

module JIRA
  module Resource
    # The attachement class
    class Attachment < JIRA::Base
      def save!(attrs, path = url)
        file = attrs['file'] || attrs[:file] # Keep supporting 'file' parameter as a string for backward compatibility
        mime_type = attrs[:mimeType] || 'application/binary'

        headers = { 'X-Atlassian-Token' => 'nocheck' }
        headers.merge!(client.options[:default_headers]) if client.options[:default_headers]

        data = { 'file' => UploadIO.new(file, mime_type, file) }

        response = client.post_multipart(path, data, headers)

        set_attributes(attrs, response)

        @expanded = false
        true
      end

      private

      def set_attributes(attributes, response)
        set_attrs(attributes, false)
        return if response.body.nil? || response.body.length < 2

        json = self.class.parse_json(response.body)
        attachment = json[0]

        set_attrs(attachment)
      end
    end
  end
end
