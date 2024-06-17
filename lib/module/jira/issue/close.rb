# frozen_string_literal: true

require 'module/jira/issue/issue_command'

module CAC
  module Jira
    # Mark a issue "Closed"
    class IssueCloseCommand < IssueCommand
      attr_accessor :issue

      register_command 'issue close' do
        desc     'Mark an issue "Done"'
        required %w[id]
      end

      register_option 'id' do
        desc    'Issue ID'
        type    'string'
        default 'PROJECT-1234'
        example 'PROJECT-1234'
      end

      def execute
        issue_transition = issue.transitions.build

        available_transitions = issue.transitions # This contains an enumerable of transitions

        closed = available_transitions.detect do |transition|
          transition.name =~ /Done/i
        end
        issue_transition.save!('transition' => { 'id' => closed.id })
      end
    end
  end
end
