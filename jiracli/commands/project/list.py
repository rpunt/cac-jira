# # frozen_string_literal: true

# require 'terminal-table'
# # require 'cac/core/module/command'
# require 'module/jira/lib/client'

# module CAC
#   module Jira
#     # List projects
#     class ProjectListCommand < CAC::Jira::Core
#       register_command 'project list' do
#         desc     'List projects'
#       end

#       def execute
#         client = Jira::Client.instance.client

#         #####################
#         # # list projects # #
#         #####################
#         logger.debug 'Listing projects'

#         begin
#           projects = client.Project.all
#         rescue JIRA::HTTPError => e
#           logger.error("#{JSON.parse(e.response.body)['errorMessages'].join(';')} (#{e.code})")
#         end

#         models = []

#         projects.each do |project|
#           model = Cac::Core::Model.new(
#             Key: project.key,
#             Name: project.name
#           )

#           models << model
#         end

#         print_models models.sort_by(&:Key)
#       end
#     end
#   end
# end
