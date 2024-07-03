# frozen_string_literal: true

require 'cac/core/module/command'
require 'module/jira/lib/client'
# require 'date'

module CAC
  module Jira
    # Create a new Jira issue
    class IssueCreateCommand < Cac::Core::Module::Command
      register_command 'issue create' do
        desc     'Create a new Jira issue'
        required %w[title description]
        optional %w[type project epic epic_name browse labels assign begin]
      end

      register_option 'title' do
        desc  'Issue title'
        short 't'
        type  'string'
      end

      register_option 'type' do
        desc           'Issue type to create'
        default        'task'
        type           'string'
        short          'y'
        allowed_values 'crdb_cluster,task,epic'
      end

      register_option 'assign' do
        desc    'Assign the issue to yourself?'
        type    'boolean'
        default false
      end

      register_option 'begin' do
        desc    'Mark issue in-progress'
        type    'boolean'
        default false
      end

      # what the...? `Error creating issue: {"customfield_11444"=>"Epic Name is required."}`
      register_option 'epic' do
        desc 'Tie this issue to an existing Epic'
        type 'string'
      end

      register_option 'labels' do
        desc     'A comma-separated list of labels to apply to the issue'
        type     'string'
        example  'label1,label2'
      end

      register_option 'epic_name' do
        desc 'Name your Epic'
        type 'string'
      end

      register_option 'description' do
        desc 'Why do we need this issue?'
        type 'string'
      end

      register_option 'browse' do
        desc   'Open the issue in your browser once created'
        type   'boolean'
        default false
      end

      def execute
        client = Jira::Client.instance.client

        projectkey = config['project'].upcase
        projectkey = opts[:project].upcase if opts[:project_given]

        begin
          client.Project.find(projectkey)
        rescue JIRA::HTTPError => e
          logger.error(JSON.parse(e.message)['errorMessages'].join("\n"))
        end

        issuetypeid = Jira::Client.instance.getIssueTypeID(opts[:type])

        fieldset = {}
        fieldset['summary'] = opts[:title]
        fieldset['description'] = opts[:description]
        fieldset['project'] = {}
        fieldset['project']['key'] = projectkey
        fieldset['issuetype'] = {}
        fieldset['issuetype']['id'] = issuetypeid

        logger.error "You're tring to link an epic to an epic" if !opts[:epic].nil? && opts[:type] == 'epic'

        unless opts[:labels].nil?
          logger.debug("Adding labels: #{opts[:labels]}")
          fieldset['labels'] = opts[:labels].split(',')
        end

        # If creating an epic, an epic name is required
        if opts[:type] == 'epic'
          if opts[:epic_name].nil?
            logger.error 'Epic Name is required if creating an Epic'
          else
            epic_name_field = client.Field.all.select { |f| f.name == 'Epic Name' }.first.id
            fieldset[epic_name_field] = opts[:epic_name]
          end
        end

        # Link a issue to an existing epic
        unless opts[:epic].nil?
          epic = opts[:epic].upcase
          begin
            client.Issue.find(epic)
          rescue JIRA::HTTPError => e
            logger.error("#{JSON.parse(e.response.body)['errorMessages'].join(';')} (#{e.code})")
          end

          epic_link_field = client.Field.all.select { |f| f.name == 'Epic Link' }.first.id
          fieldset[epic_link_field] = epic
        end

        issue = client.Issue.build
        issue.save('fields' => fieldset)

        if issue.respond_to? :errors
          logger.error("Error creating issue: #{issue.errors['issuetype']}")
        else
          logger.info("Created Jira #{opts[:type]}: #{issue.key}")
        end

        call_module_command('jira', 'issue assign',     id: issue.key, suppress_output: true) if opts[:assign]
        call_module_command('jira', 'issue begin',      id: issue.key, suppress_output: true) if opts[:begin]
        call_module_command('jira', 'issue browse',     id: issue.key, suppress_output: true) if opts[:browse]
      end

      def setup
        opts[:assign]     = true if opts[:begin]

        # can't gsub! -- throws cannot modify frozen string
        # Optimist or something is escaping \ so "testing\nwith\nnew lines" turns into "Testing\\nwith\\nnewlines"
        opts[:description] = opts[:description].gsub('\\n', "\n")
      end
    end
  end
end
