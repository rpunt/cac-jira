# frozen_string_literal: true

lib = File.expand_path('lib', __dir__)
$LOAD_PATH.unshift(lib) unless $LOAD_PATH.include?(lib)
require 'module/jira/version'

Gem::Specification.new do |s|
  s.name    = 'cac-jira'
  s.version = CAC::Jira::VERSION
  s.authors = ['Ryan Punt']
  s.email   = ['ryan@mirum.org']

  s.summary     = 'Interact with Jira'
  s.description = 'Interact with Jira'
  s.homepage    = 'https://github.com/rpunt/cac-jira'
  s.license     = 'Apache-2.0'

  s.files         = Dir.glob('lib/**/*') + %w[cac-jira.gemspec]
  s.require_paths = %w[lib]

  s.required_ruby_version = '>= 3.1'

  s.metadata['rubygems_mfa_required'] = 'true'
end
