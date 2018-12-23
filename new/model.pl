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
  my $action = shift;
  if ($action eq 'scrape') {
    shift(@doc_vector);
    shift(@subjects);
    my $json = encode_json({bodies => \@doc_vector, subjects => \@subjects});
    print $json;
  } else {
    use DBI;
    my $dbname = 'email_classifier';
    my $host = 'localhost';
    my $port = 5432;
    my $username = 'ideanlabib';
    my $password = '';
    my $dbh = DBI -> connect("dbi:Pg:dbname=$dbname;host=$host;port=$port",  
                          $username,
                          $password,
                          {AutoCommit => 0, RaiseError => 1}
                       ) or die $DBI::errstr;

    my $i = 0;
    while ($i < scalar(@emails)) {
      my $sth = $dbh->prepare("SELECT label FROM emails WHERE bodies=?");
      $sth->bind_param( 1, $doc_vector[$i + 1]);
      $sth->execute();
      
      if (my $ref = $sth->fetchrow_hashref()) {
        if ($emails[$i]->as_string =~ /(Production|Staging) Exception/) {
          print $doc_vector[$i + 1];
        }
        my $filename = "out/$ref->{'label'}.mbox";
        open(my $fh, '>>', $filename) or die "Could not open file '$filename' $!";
        print $fh $emails[$i]->as_string;
        print "label = $ref->{'label'}\n";
        close $fh;
      }

      $i++;
    }
    $dbh->disconnect;
  }
}

1;
