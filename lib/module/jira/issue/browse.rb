# frozen_string_literal: true

require 'module/jira/issue/issue_command'

module CAC
  module Jira
    # Display selected issue in your default browser
    class IssueBrowseCommand < IssueCommand
      attr_accessor :issue

      register_command 'issue browse' do
        desc        'Display selected issue in your default browser'
        required    'id'
      end

      register_option 'id' do
        desc    'Issue ID'
        type    'string'
        example 'PROJECT-1234'
      end

      def execute
        issue_link = "#{issue.self.split('/rest/api')[0]}/browse/#{issue.key}"

        logger.debug "Opening #{issue.key} in your browser"

        case RbConfig::CONFIG['host_os']
        when /darwin/
          system "open #{issue_link}"
        when /linux|bsd/
          logger.info "You're on Linux. this might work..."
          system "xdg-open #{issue_link}"
        when /mswin|mingw|cygwin/
          logger.error 'Sorry, Windows not supported at this time'
        else
          logger.error "Unknown platform detected. I show your platform as '#{RbConfig::CONFIG['host_os']}'."
        end
      end
    end
  end
end
