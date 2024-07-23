# frozen_string_literal: true

require 'module/jira/lib/client'
require 'module/jira/issue/issue_command'

module CAC
  module Jira
    # Assign an issue to yourself
    class IssueAssignCommand < IssueCommand
      attr_accessor :client, :issue, :issueID

      register_command 'issue assign' do
        desc     'Assign an issue to yourself'
        required %w[id]
      end

      register_option 'id' do
        desc    'Issue ID'
        type    'string'
        default 'PROJECT-1234'
        example 'PROJECT-1234'
      end

      def execute
        issue.save({'fields' => {'assignee' => {'accountId' => client.User.myself.accountId}}})

        if issue.respond_to? :errors
          logger.error("Error assigning #{issueID}: #{issue.errors['assignee']}")
        else
          logger.info("#{issueID} assigned to #{client.options[:username]}")
        end
      end
    end
  end
end
