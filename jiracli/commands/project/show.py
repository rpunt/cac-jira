# # frozen_string_literal: true

# require 'terminal-table'
# # require 'cac/core/module/command'
# require 'module/jira/lib/client'

# module CAC
#   module Jira
#     # List projects
#     class ProjectShowCommand < CAC::Jira::Core
#       register_command 'project show' do
#         desc     'Show project'
#         required %w[project]
#       end

#       def execute
#         client = Jira::Client.instance.client

#         ####################
#         # # show project # #
#         ####################
#         project_key = opts[:project].upcase
#         logger.debug "Showing project #{project_key}"

#         begin
#           project = client.Project.find(project_key)
#         rescue JIRA::HTTPError => e
#           logger.error("#{JSON.parse(e.response.body)['errorMessages'].join(';')} (#{e.code})")
#         end

#         models = []
#         models << Cac::Core::Model.new(
#           ID: project.id,
#           Key: project.key,
#           Name: project.name
#         )
#         print_models models.sort_by(&:Key)
#       end
#     end
#   end
# end
