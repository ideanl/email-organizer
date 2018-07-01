#!/usr/bin/local/perl
use strict;
use warnings;

use Mail::Mbox::MessageParser;
use Email::MIME;
use HTML::Parser;
use HTML::Entities;
use Encode qw(encode);

require './model.pl';

my $file_name = shift(@ARGV) || "Archived.mbox";
print $file_name, "\n";
#my $file_name = "input.tgz";
my $file_handle = new FileHandle($file_name);

Mail::Mbox::MessageParser::SETUP_CACHE(
  { 'file_name' => '/tmp/cache' } );


my $parser = HTML::Parser->new(api_version => 3);
$parser->handler(text => \&process_html_text, 'text');
 
my $folder_reader =
  new Mail::Mbox::MessageParser( {
    'file_name' => $file_name,
    'file_handle' => $file_handle,
    'enable_cache' => 1,
    'enable_grep' => 1,
  } );

die $folder_reader unless ref $folder_reader;

my $i = 0;
while($i < 200 && !$folder_reader->end_of_file()) {
	my $email = $folder_reader->read_next_email();
	$email = Email::MIME->new($email);
  new_doc($email, encode('UTF-8', $email->header('Subject')));
  process_email($email);
  $i++;
}

out_data();

sub process_email {
  my $email = shift;

  for my $part ($email->parts) {
    if ($part->content_type =~ m!multipart/alternative! or $part->content_type eq '' ) {
      for my $subpart ($part->parts) {
        if ($subpart->content_type) {
          process_body($subpart->body, $subpart->content_type);
        }
      }
    } else {
      if ($part->content_type) {
        process_body($part->body, $part->content_type);
      }
    }
  }
}

sub process_body {
  my $body = shift;
  my $type = shift;

  if ($type =~ /(text\/plain)/) {
    # Filter whitespace including decoded &nbsp
    process_text($body);
  } elsif ($type =~ /text\/html/) {
    $parser->parse($body);
  }
}

sub process_html_text {
  my $text = decode_entities(shift);

  process_text($text);
}

sub process_text {
  my $text = shift;

  $text =~ s/[^A-Za-z\s]//g;

  if ($text ne "") {
    # replace with doc-term matrix
    addToDoc(encode('UTF-8', $text));
  }
}
