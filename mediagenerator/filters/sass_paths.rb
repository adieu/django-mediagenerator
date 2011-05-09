require "rubygems"
require "sass"
require "compass"

DEFAULT_FRAMEWORKS = ["compass", "blueprint"]

ARGV.each do |arg|
  next if arg == "compass"
  next if arg == "blueprint"
  require arg
end

Compass::Frameworks::ALL.each do |framework|
  next if framework.name =~ /^_/
  next if DEFAULT_FRAMEWORKS.include?(framework.name) && !ARGV.include?(framework.name)
  print "#{File.expand_path(framework.stylesheets_directory)}\n"
end
