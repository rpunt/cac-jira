# frozen_string_literal: true

require 'module/jira/issue/issue_command'

module CAC
  module Jira
    # Mark a issue "in-progress"
    class IssueBeginCommand < IssueCommand
      attr_accessor :issue

      register_command 'issue begin' do
        desc     'Mark an issue "in-progress"'
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

        prioritized = available_transitions.detect do |transition|
          transition.name =~ /In Progress/i
        end
        issue_transition.save!('transition' => { 'id' => prioritized.id })
      end
    end
  end
end
