# frozen_string_literal: true

require 'terminal-table'
require 'module/jira/issue/issue_command'

module CAC
  module Jira
    # Delete a issue
    class IssueDeleteCommand < IssueCommand
      attr_accessor :issue

      register_command 'issue delete' do
        desc     'Delete a issue'
        required %w[id]
      end

      register_option 'id' do
        desc    'Issue ID'
        type    'string'
        default 'PROJECT-1234'
        example 'PROJECT-1234'
      end

      def execute
        logger.error 'Delete of issue failed' unless issue.delete
        logger.info 'Delete of issue succeeded'
      end
    end
  end
end
