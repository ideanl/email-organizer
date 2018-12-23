use strict;
use warnings;

my @emails = ();
my @doc_vector = ();
my %terms = ();
my @subjects = ();

push @doc_vector, {};
push @subjects, "";

sub new_doc {
  my $email = shift;
  my $subject = shift;
  push @emails, $email;
  push @doc_vector, {};
  push @subjects, ($subject || "");
}

sub addToDoc {
  my $body = shift;
  my $docn = scalar(@doc_vector) - 1;
  
  my @words = split /\s+/, $body;
  foreach my $word (@words) {
    add_word($word, $docn)
  }
}

sub add_word {
  my $word = shift;
  my $docn = shift;
  my $weight = shift || 1;

  chomp $word;

  $terms{$word} = 1;
  $doc_vector[$docn]{$word} += $weight;
}

sub out_data {
  open OUT, ">data.out";
  foreach my $term (keys %terms) {
    for my $docn ( 1 .. scalar(@doc_vector) - 1) {
      print OUT %{$doc_vector[$docn]}{$term} || 0;
      if ($docn != scalar(@doc_vector) - 1) {
        print OUT ",";
      } else {
        print OUT "\n";
      }
      $docn++;
    }
  }
  close OUT;
  
  open SUBJ_OUT, ">subjects.out";
  for my $docn ( 1 .. scalar(@doc_vector) - 1) {
    $subjects[$docn] =~ s/^\s*$/No Subject/g;
    print SUBJ_OUT $subjects[$docn], "\n";
  }
  close SUBJ_OUT;
}

1;
