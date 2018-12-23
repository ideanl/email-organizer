use strict;
use warnings;

use JSON;

my @emails = ();
my @doc_vector = ();
my @subjects = ();
my %terms = ();

push @doc_vector, "";
push @subjects, "";

sub new_doc {
  my $email = shift;
  push @emails, $email;
  push @doc_vector, "";
  push @subjects, encode('UTF-8', $email->header('Subject'));
}

sub addToDoc {
  my $body = shift;
  $doc_vector[scalar(@doc_vector) - 1] .= $body;
}

sub out_data {
  shift(@doc_vector);
  shift(@subjects);
  my $json = encode_json({bodies => \@doc_vector, subjects => \@subjects});
  print $json;
}

1;
