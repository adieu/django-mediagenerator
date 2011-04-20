require "rubygems"
require "sass"
require "compass"

ARGV.each do |arg|
  require arg
end

Compass::Frameworks::ALL.each do |framework|
  next if framework.name =~ /^_/
  print "#{File.expand_path(framework.stylesheets_directory)}\n"
end
