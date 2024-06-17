# frozen_string_literal: true

require 'cac/core/module'
require 'module/jira/version'

module CAC
  # The Jira module for CAC
  module Jira
    extend Cac::Core::Module

    COMMAND = 'jira'
    DESC = 'Jira Integration'
    MAINTAINER = 'Ryan Punt'
    MAINTAINER_EMAIL = 'ryan@mirum.org'

    register_module

    register_option 'project' do
      desc    'The Jira project to use'
      type    'string'
    end
  end
end
