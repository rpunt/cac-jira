# frozen_string_literal: true

require 'terminal-table'
# require 'cac/core/module/command'
require 'module/jira/lib/client'

module CAC
  module Jira
    # List stories by project
    class IssueListCommand < CAC::Jira::Core
      register_command 'issue list' do
        desc     'List issues by project'
        optional %w[project mine done]
      end

      register_option 'mine' do
        desc    'Show only my issues'
        type    'boolean'
        default false
      end

      register_option 'done' do
        desc           'Include issues marked "Done"'
        default        false
        type           'boolean'
      end

      def execute
        client = Jira::Client.instance.client

        projectkey = config['project']
        projectkey = opts[:project] if opts[:project_given]

        logger.debug "Listing stories for project #{projectkey}"

        ###############################
        # # list issues by project # #
        ###############################
        models = []

        jql_query = []
        jql_query << 'assignee = currentUser()' if opts[:mine]
        jql_query << 'Status != Done' unless opts[:done]

        issues = call_module_command('jira', 'issue search', { project: projectkey, jql: jql_query.join(' and '), fields: 'key,summary,status,assignee,issuetype' })

        issues.each do |issue|
          assignee = issue.assignee.nil? ? 'unassigned' : issue.assignee.displayName

          model = Cac::Core::Model.new(
            ID: issue.key,
            Type: issue.issuetype.name,
            Summary: issue.summary,
            Status: issue.status.name,
            Assignee: assignee
          )

          models << model
        end
        print_models models
      end
    end
  end
end
