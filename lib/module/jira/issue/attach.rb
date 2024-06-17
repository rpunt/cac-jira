# frozen_string_literal: true

# require 'cac/core/module/command'
require 'module/jira/lib/client'

module CAC
  module Jira
    # Attach a file to a issue
    class IssueAttachCommand < CAC::Jira::Core
      register_command 'issue attach' do
        desc     'Attach a file to an issue'
        required %w[id file]
      end

      register_option 'id' do
        desc    'Issue ID'
        type    'string'
        default 'PROJECT-1234'
        example 'PROJECT-1234'
      end

      register_option 'file' do
        desc           'File to attach'
        default        ''
        type           'string'
        example        'test.txt'
      end

      def execute
        client = Jira::Client.instance.client

        begin
          issue = client.Issue.find(opts[:id].upcase)
        rescue JIRA::HTTPError => e
          logger.error("#{JSON.parse(e.response.body)['errorMessages'].join(';')} (#{e.code})")
        end

        attachment = JIRA::Resource::Attachment.new(client, issue:)

        begin
          attachment.save!(file: opts[:file])
        rescue JIRA::HTTPError => e
          logger.error("#{JSON.parse(e.response.body)['errorMessages'].join(';')} (#{e.code})")
        rescue Errno::ENOENT => e
          logger.error("Generic error: #{e}")
        end
      end
    end
  end
end
