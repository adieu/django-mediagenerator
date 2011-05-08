require "rubygems"
require "compass"

module Compass::SassExtensions::Functions::Urls

  def stylesheet_url(path, only_path = Sass::Script::Bool.new(false))
    if only_path.to_bool
      Sass::Script::String.new(clean_path(path))
    else
      clean_url(path)
    end
  end

  def font_url(path, only_path = Sass::Script::Bool.new(false))
    path = path.value # get to the string value of the literal.

    # Short curcuit if they have provided an absolute url.
    if absolute_path?(path)
      return Sass::Script::String.new("url(#{path})")
    end

    if only_path.to_bool
      Sass::Script::String.new(clean_path(path))
    else
      clean_url(path)
    end
  end

  def image_url(path, only_path = Sass::Script::Bool.new(false))
    print "#{@options}\n"
    path = path.value # get to the string value of the literal.

    if absolute_path?(path)
      # Short curcuit if they have provided an absolute url.
      return Sass::Script::String.new("url(#{path})")
    end

    if only_path.to_bool
      Sass::Script::String.new(clean_path(path))
    else
      clean_url(path)
    end
  end

  private

  # Emits a path, taking off any leading "./"
  def clean_path(url)
    url = url.to_s
    url = url[0..1] == "./" ? url[2..-1] : url
  end

  # Emits a url, taking off any leading "./"
  def clean_url(url)
    Sass::Script::String.new("url('#{clean_path(url)}')")
  end

  def absolute_path?(path)
    path[0..0] == "/" || path[0..3] == "http"
  end

end

module Sass::Script::Functions
  include Compass::SassExtensions::Functions::Urls
end
