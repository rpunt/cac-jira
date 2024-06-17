# frozen_string_literal: true

require 'module/jira/issue/issue_command'
require 'terminal-table'
require 'date'

module CAC
  module Jira
    # Show a Jira issue
    class IssueShowCommand < IssueCommand
      attr_accessor :issue

      register_command 'issue show' do
        desc     'Show a Jira issue'
        required %w[id]
      end

      register_option 'id' do
        desc    'Issue ID'
        type    'string'
        example 'PROJECT-1234'
      end

      def execute
        if opts[:json]
          puts issue.to_json
        elsif issue.attrs['fields']['issuetype']['id'].to_i == 21_686
          output_crdb_cluster_table(issue)
        else
          output_table(issue)
        end
      end

      private

      def output_crdb_cluster_table(issue)
        assignee = 'Unassigned'
        assignee = issue.assignee.attrs['displayName'] unless issue.assignee.nil?
        table_width = issue.comments.count.positive? ? 150 : nil

        table = Terminal::Table.new do |t|
          t.style = { width: table_width }
          t.add_row [{ value: issue.attrs['fields']['issuetype']['name'], alignment: :right }, issue.attrs['key']]
          t.add_row [{ value: 'Assignee', alignment: :right }, assignee]
          t.add_row [{ value: 'Status', alignment: :right }, issue.attrs['fields']['status']['name']]
          t.add_separator

          t.add_row [
            { value: 'Summary', alignment: :right },
            issue.attrs['fields']['summary']
          ]
          t.add_separator

          # t.add_row [
          #   { value: 'Description', alignment: :right },
          #   { value: wrap_string(issue.attrs['fields']['description'], 110) }
          # ]
          # t.add_separator

          t.add_row [{ value: 'Anticipated QPS', alignment: :left }, {}]
          # "customfield_24007": 1.0,
          t.add_row [
            { value: 'Read', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24007'], 110) }
          ]
          # "customfield_24008": 2.0,
          t.add_row [
            { value: 'Write', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24008'], 110) }
          ]
          # "customfield_24009": 3.0,
          t.add_row [
            { value: 'Update', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24009'], 110) }
          ]
          # "customfield_24010": 4.0,
          t.add_row [
            { value: 'Delete', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24010'], 110) }
          ]
          t.add_separator

          t.add_row [{ value: 'Anticipated throughput', alignment: :left }, {}]
          # "customfield_24011": 5.0,
          t.add_row [
            { value: 'Read', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24011'], 110) }
          ]
          # "customfield_24012": 6.0,
          t.add_row [
            { value: 'Write', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24012'], 110) }
          ]
          # "customfield_24013": 7.0,
          t.add_row [
            { value: 'Update', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24013'], 110) }
          ]
          # "customfield_24014": 8.0,
          t.add_row [
            { value: 'Delete', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24014'], 110) }
          ]
          t.add_separator

          t.add_row [{ value: 'Business Use', alignment: :left }, {}]
          # "customfield_24018": "expected data size",
          t.add_row [
            { value: 'Expected Data Size', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24018'], 110) }
          ]

          # "customfield_24016": "required sla",
          t.add_row [
            { value: 'Required SLA', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_24016'], 110) }
          ]

          # geographically distributed:
          # "customfield_24017": {
          #   "self": "https://doordash.atlassian.net/rest/api/2/customFieldOption/48796",
          #   "value": "Yes",
          #   "id": "48796"
          # },
          unless issue.attrs['fields']['customfield_24017'].nil?
            t.add_row [
              { value: 'Clients are geographically distributed', alignment: :right },
              { value: wrap_string(issue.attrs['fields']['customfield_24017']['value'], 110) }
            ]
            t.add_separator
          end

          t.add_row [
            { value: 'Okta Username', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23853'], 110) }
          ]

          t.add_row [
            { value: 'Service Tag', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23856'], 110) }
          ]

          t.add_row [
            { value: 'Team Name', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23854'], 110) }
          ]

          t.add_row [
            { value: 'Project Name', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23852'], 110) }
          ]

          t.add_row [
            { value: 'Team DRI', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23857'], 110) }
          ]

          t.add_row [
            { value: 'Team Okta Group', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23860'], 110) }
          ]

          t.add_row [
            { value: 'Team DDPD Alias', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23858'], 110) }
          ]

          t.add_row [
            { value: 'Team Slack Channel', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23859'], 110) }
          ]

          t.add_row [
            { value: 'Tier', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23863']['value'], 110) }
          ]

          t.add_row [
            { value: 'Environment', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23861']['value'], 110) }
          ]

          t.add_row [
            { value: 'Team Terraform Directories', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23862'], 110) }
          ]

          t.add_row [
            { value: 'Service Name', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23865'], 110) }
          ]

          t.add_row [
            { value: 'Service Language', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23866'], 110) }
          ]

          t.add_row [
            { value: 'Service Location', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23867']['value'], 110) }
          ]

          t.add_row [
            { value: 'Team Email', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23855'], 110) }
          ]

          t.add_row [
            { value: 'The workload is', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['customfield_23868']['value'], 110) }
          ]

          if issue.attrs['fields']['customfield_23868']['value'] == 'Existing'
            t.add_row [
              { value: 'This workload is coming from', alignment: :right },
              { value: wrap_string(issue.attrs['fields']['customfield_23869'], 110) }
            ]
          end
        end
        puts table
      end

      def output_table(issue)
        assignee = 'Unassigned'
        assignee = issue.assignee.attrs['displayName'] unless issue.assignee.nil?
        table_width = issue.comments.count.positive? ? 150 : nil

        table = Terminal::Table.new do |t|
          t.style = { width: table_width }
          t.add_row [{ value: issue.attrs['fields']['issuetype']['name'], alignment: :right }, issue.attrs['key']]
          t.add_row [{ value: 'Assignee', alignment: :right }, assignee]
          t.add_row [{ value: 'Status', alignment: :right }, issue.attrs['fields']['status']['name']]
          t.add_separator
          t.add_row [
            { value: 'Summary', alignment: :right },
            issue.attrs['fields']['summary']
          ]
          t.add_separator
          t.add_row [
            { value: 'Description', alignment: :right },
            { value: wrap_string(issue.attrs['fields']['description'], 110) }
          ]

          if issue.comments.count.positive?
            t.add_separator
            t.add_row [
              { value: 'Comments', alignment: :center, colspan: 2 }
            ]
            t.add_separator
            issue.comments.each do |comment|
              t.add_row [
                { value: "#{comment.attrs['author']['displayName']}\n#{DateTime.parse(comment.created).strftime('%Y-%m-%d %H:%M:%S')}" },
                { value: wrap_string(comment.attrs['body'], 110) }
              ]
              t.add_separator
            end
            # {:value => wrap_string(issue.attrs['fields']['comment']['comments'].count, 110)}
          end
        end
        puts table
      end

      # https://github.com/tj/terminal-table/issues/1
      def wrap_string(s, max)
        s = 'Not Specified' if s.nil?
        chars = []
        dist = 0
        s.to_s.chars.each do |c|
          chars << c unless c == "\r"
          dist += 1
          if c == "\n"
            dist = 0
          elsif dist == max
            dist = 0
            chars << "\n"
          end
        end
        chars = chars[0..-2] if chars.last == "\n"
        chars.join
      end
    end
  end
end
