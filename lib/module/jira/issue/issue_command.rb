# frozen_string_literal: true

# require 'cac/core/module/command'
require 'module/jira/lib/client'

module CAC
  module Jira
    # the base class for single-issue Jira commands
    class IssueCommand < CAC::Jira::Core
      def setup
        @client = Jira::Client.instance.client

        @client.http_debug = opts[:verbose]

        @issueID = opts[:id].upcase

        begin
          @issue = @client.Issue.find(@issueID, { expand: 'transitions' })
        rescue JIRA::HTTPError => e
          logger.error("#{JSON.parse(e.response.body)['errorMessages'].join(';')} (#{e.code})")
        end
      end
    end
  end
end
