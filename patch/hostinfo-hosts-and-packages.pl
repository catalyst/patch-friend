#!/usr/bin/perl -T

# Generate JSON output for all the host variables + all the packages installed on each host. Used by patch-friend.

use strict;
use warnings;

use CGI;
use Hostinfo::DB;
use JSON;
use Data::Dumper;

my $cgi = new CGI();

print $cgi->header(-type=>"application/json",charset=>'utf-8');

my $schema = Hostinfo::DB->getSchema();

my $hosts = $schema->resultset('Host')->search(
    {},
    {
        columns  => [ qw/hostid hostname hardware release updated fingerprint/ ],
    },
);

print "{\n";
my $first = 1;
my %packages;
while (my $host = $hosts->next) {
    if ($first == 1) {
        print "    ";
        $first = 0;
    } else {
        print ",\n    ";
    }

    my @packages;
    my @machineinfo;
    my %metadata;
    my $packages = $host->search_related('packages', {}, {
        columns => [ qw/package status version/ ],
    });

    my $machineinfo = $host->search_related('cat_machineinfos', {}, {
        columns => [ qw/key value/ ],
    });

    while (my $p = $packages->next) {
        push @packages, { name => $p->package, status => $p->status, version => $p->version };
    }

    while (my $m = $machineinfo->next) {
        push @machineinfo, { key => $m->key, value => $m->value };
    }

    $metadata{hostid} = $host->hostid;
    $metadata{hardware} = $host->hardware;
    $metadata{release} = $host->release;
    $metadata{updated} = $host->updated;
    $metadata{fingerprint} = $host->fingerprint;

    my $object = {
        $host->hostname => {
            packages => \@packages,
            metadata => \%metadata,
            machineinfo => \@machineinfo,
        },
    };

    my $json = encode_json($object);
    $json =~ s/^{//;
    $json =~ s/}$//;
    print $json;
}
#my $json = encode_json(\%packages);
#print $json;
print "\n}";

