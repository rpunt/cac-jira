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
        assignee = client.options[:username]

        issue.save({ 'fields' => { 'assignee' => { 'name' => assignee } } })

        if issue.respond_to? :errors
          logger.error("Error assigning #{issueID}: #{issue.errors['assignee']}")
        else
          logger.info("#{issueID} assigned to #{assignee}")
        end
      end
    end
  end
end
