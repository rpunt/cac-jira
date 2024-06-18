# frozen_string_literal: true

require 'terminal-table'
# require 'cac/core/module/command'
require 'module/jira/lib/client'

module CAC
  module Jira
    # Search for a JIRA issue using JQL
    class IssueSearchCommand < CAC::Jira::Core
      DEFAULT_JQL_FIELDS = %i[description summary issuetype status assignee created labels].freeze

      register_command 'issue search' do
        desc     'Search for a JIRA issue using JQL'
        required %w[jql]
        optional %w[fields project]
      end

      register_option 'jql' do
        desc    'JQL query'
        type    'string'
        example 'text ~ "Renew" AND  labels = CertRenewals AND created >= -20d'
      end

      register_option 'fields' do
        desc    'Comma separated JIRA fields to restrict JQL returned result.'
        type    'string'
        example 'description,summary,labels,created'
      end

      def execute
        client = Jira::Client.instance.client

        jql_fields = opts[:fields].nil? ? DEFAULT_JQL_FIELDS : opts[:fields].split(',').map(&:to_sym)
        jql = ["project = \"#{opts[:project]}\""]
        jql << "#{opts[:jql]}" unless opts[:jql].empty?
        logger.debug "Performing JIRA search with JQL [#{jql}] and selected fields are #{jql_fields}"

        begin
          jql_search = client.Issue.jql(jql.join(' and '), fields: jql_fields, max_results: 5000)
        rescue JIRA::HTTPError => e
          logger.error("#{JSON.parse(e.response.body)['errorMessages'].join(';')} (#{e.code})")
        end

        return jql_search if opts[:external_call]

        if opts[:json]
          puts jql_search.to_json
        else
          jql_search.each do |issue|
            output_table(issue)
          end
        end
      end

      private

      def output_table(issue)
        table_width = issue.comments.count.positive? ? 150 : nil
        table = Terminal::Table.new do |t|
          t.style = { width: table_width }
          t.add_row [{ value: issue.attrs['fields']['issuetype']['name'], alignment: :right }, issue.attrs['key']]
          t.add_row [{ value: 'Status', alignment: :right }, issue.attrs['fields']['status']['name']]
          t.add_row [
            { value: 'Summary', alignment: :right },
            issue.attrs['fields']['summary']
          ]
          t.add_row [{ value: 'Labels', alignment: :right }, issue.attrs['fields']['labels'].join(', ')]
        end
        puts table
      end
    end
  end
end
