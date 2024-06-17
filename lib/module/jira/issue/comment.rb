# frozen_string_literal: true

require 'module/jira/issue/issue_command'

module CAC
  module Jira
    # comment on an issue
    class IssueCommentCommand < IssueCommand
      attr_accessor :issue

      register_command 'issue comment' do
        desc     'Comment on a issue'
        required %w[id comment]
        optional %w[close]
      end

      register_option 'id' do
        desc    'Issue ID'
        type    'string'
        default 'PROJECT-1234'
        example 'PROJECT-1234'
      end

      register_option 'comment' do
        desc           'Comment to add'
        default        ''
        type           'string'
        example        'A Comment'
      end

      register_option 'close' do
        desc           'Close a issue after commenting'
        type           'boolean'
        default        false
      end

      def execute
        comment = issue.comments.build
        comment.save!(body: opts[:comment])

        call_module_command('jira', 'issue close', id: issue.key, suppress_output: true) if opts[:close]
      end
    end
  end
end
