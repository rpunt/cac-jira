# frozen_string_literal: true

require 'rubygems'
require 'rubygems/specification'
require 'bundler/gem_tasks'
require 'json'
require 'rest-client'
require 'rubocop/rake_task'
require 'rspec/core/rake_task'

def gemspec
  @gemspec ||= begin
    gemspec = Dir[File.join(__dir__, '{,*}.gemspec')].first
    Bundler.load_gemspec(gemspec)
  end
end

def name_version
  "#{gemspec.name}-#{gemspec.version}"
end

RuboCop::RakeTask.new(:lint) do |t|
  t.options = ['-fg', 'lib', 'Rakefile']
end

task default: :lint

desc 'Output gem version'
task :version do
  puts gemspec.version
end

# desc 'Output gem name'
task :spec do
  RSpec::Core::RakeTask.new(:spec)
end
