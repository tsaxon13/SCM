#!/usr/bin/perl

# Pidgeon - a cgi web interface for storing system changes in a database.
# Written by Tony Saxon
# 2/15/04



use CGI;
use DBI;
use Net::LDAP;
use Time::Local;
use strict;

########################## Global Variables ####################################

# Ldap settings
my $LDAP_server = "ldap.fccc.edu";
my $LDAP_base = "ou=People,o=Fox Chase Cancer Center,c=US";

# Database Settings
# Values of $database can be Oracle or mysql
my $database= "Oracle";
my $dbhost="scmdb";
my $sid="oracle";
my $dbuser = '';
my $dbpass = '';
my $dsn;


$ENV{'LD_LIBRARY_PATH'}="/usr/oracle/lib";
$ENV{'ORACLE_HOME'}="/usr/oracle";
$ENV{'TWO_TASK'} = "scmdb";
$ENV{'ORACLE_SID'} = "scmdb";


if ($database eq "mysql"){
	$dsn = 'dbi:'.$database.':database='.$sid.';host='.$dbhost;
} else {
	$dsn = 'dbi:'.$database.":$dbhost";
}

my $dbh = DBI->connect($dsn, $dbuser, $dbpass)
        or die $DBI::errstr;



# Session variables
my $session = new CGI;

#set Date format
if ($database eq "Oracle"){
	my $sqldate =  "alter session set NLS_DATE_FORMAT=\'YYYY-MM-DD HH24:MI\'";
	my $sthdate = $dbh->prepare($sqldate);
	$sthdate->execute();
}
#################################################################################

# Begin definition of program subroutines.
# Edit at your own risk.

sub htmlHeader {

	my $error = $_[0];
	
	if ($session->param('login') && !$session->param('logout')){
		print "Content-type:text/html\n";
		print "Set-Cookie: uid=".$session->param('uid').";\n";
		print "Set-Cookie: pass=".$session->param('pass').";\n";
		print "Set-Cookie: login=".$session->param('login')."\n";
	} elsif ($session->param('logout')){
		print "Content-type:text/html\n";
		print "Set-Cookie: uid=;\n";
		print "Set-Cookie: pass=;\n";
		print "Set-Cookie: login=\n";
	} else {
		print "Content-type:text/html\n";
	}

	print 	"Pragma: no-cache\n",
		"Expires: -1\n",
		"Cache-Control: no-store, no-cache, must-revalidate\n\n";
	print<<ENDY;
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<title>System Change Manager</title>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="-1">
<meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate">
<style type="text/css">
<!--
body { background-color: #fff; color: #000; font-family: verdana, arial, sans-serif; }
form { margin-bottom: 3px; }
#disclaimer { border: 0px solid #000; padding: 5px; background-color: #fff; font-size: 12px; }
#form { width: 75%; border: 1px solid #000; padding: 5px; padding-bottom: 0px; background-color: #ddd; font-size: 14px; }
#loginform { width: 400px; border: 1px solid #000; padding: 5px; padding-bottom: 0px; background-color: #ddd; font-size: 14px; }
.error { color: #f00; font-size: 16px; }
-->
</style>
</head>
<body>
ENDY
;

	if( $error ) {
		print '<p class="error">'. $error ."</p>"
	}

	print '<div align=center>';
}

sub htmlFrame {

	print<<ENDY;
<table nowrap frame="void" width="100%">
<tr>
ENDY
;
}

sub htmlMenu {

	print<<ENDY;
<td valign=top width="20%">
<pre>
<a href="/cgi-bin/pidgeon.cgi?search=Search">Search</a>     <a href="/cgi-bin/pidgeon.cgi?add=Add">Add new Entry</a>     <a href="/cgi-bin/pidgeon.cgi?addSystem=add">Add new System</a>     <a href="/cgi-bin/pidgeon.cgi">Home</a>     <a href="/cgi-bin/pidgeon.cgi?logout=Logout">Logout</a>
</pre>
<hr>
ENDY
;

print 	"</td>\n</tr>\n<tr>",
	"<td>\n";

}

sub htmlEndTable {

	print<<ENDY;
</td>
</tr>
</table>
ENDY
;
}

sub htmlLogin {
	my $uid = $_[0];
	
	print<<ENDY;
<p>Please login to System Change Manager.</p>

<div id="loginform" align=left>
<form name="loginform" method="post" action="/cgi-bin/pidgeon.cgi"/>
<table width="100%" cellpadding="2" cellspacing="1" summary="Login Form" style="margin-bottom: 0px;">
<tr>
<td width="50%;" align="right">User Name</td>
<td width="50%;" align="left"><input size="10" type="text" name="uid" value="$uid" /> </td>
</tr>

<tr>
<td width="50%;" align="right">Password</td>
<td width="50%;" align="left"><input size="10" type="password" name="pass" /> </td>
</tr>

<tr>
<td colspan="2" align="center"><input type="submit" name="login" value="Login" /> </td>
</tr>
</table>
</form>
</div>
ENDY
;
}

sub LDAPLogin {
	my $uid = $_[0];
	my $pass = $_[1];
	my $ldap;

	$ldap = Net::LDAP->new( $LDAP_server );
	my $result = $ldap->bind( "uid=$uid, $LDAP_base", password => $pass );

	return $result;
}

sub getYear {

	my $string = scalar localtime;
	my @rawdate = split(" ",$string);

	return @rawdate[4];
}

sub currentDate {
	my @rawdate = split(" ",scalar localtime);
	my @rawtime = split(":",$rawdate[3]);
	my $month;

	if ($rawdate[1] eq "Jan"){ #set number of month
		$month = "01";
	} elsif ($rawdate[1] eq "Feb"){
		$month = "02";
	} elsif ($rawdate[1] eq "Mar"){
		$month = "03";
	} elsif ($rawdate[1] eq "Apr"){
		$month = "04";
	} elsif ($rawdate[1] eq "May"){
		$month = "05";
	} elsif ($rawdate[1] eq "Jun"){
                $month = "06";
	} elsif ($rawdate[1] eq "Jul"){
                $month = "07";
	} elsif ($rawdate[1] eq "Aug"){
                $month = "08";
	} elsif ($rawdate[1] eq "Sep"){
                $month = "09";
	} elsif ($rawdate[1] eq "Oct"){
                $month = "10";
	} elsif ($rawdate[1] eq "Nov"){
                $month = "11";
	} elsif ($rawdate[1] eq "Dec"){
                $month = "12";
	}


	my $date = $rawdate[4]."-".$month."-".$rawdate[2]." ".$rawtime[0].":".$rawtime[1];

	return $date;
}

sub systemHash {

	my $query = "select * from systems";
                                                                                                                                                              
	my $sth = $dbh->prepare($query);

	$sth->execute();
	
	my %syshash;

	while (my @syshash_ref = $sth->fetchrow_array) {
		$syshash{$syshash_ref[0]} = $syshash_ref[1];
	}
	if ($sth->err) {
		print "Error: ",$sth->err,"\n";
		exit (0);
	}

	return %syshash;
}

sub sysnumArray {

	my $query = "select * from systems order by system";
	my $sth = $dbh->prepare($query);

	$sth->execute();

	my $i=0;
	my @systems;

	while (my @syshash_ref = $sth->fetchrow_array) {
		$systems[$i]=$syshash_ref[0];
		$i = $i+1;
	}
	if ($sth->err) {
		print "Error: ", $sth->err,"\n";
		exit(0);
	}

	return @systems;
}

sub systemArray {
                                                                                                                                                             
        my $query = "select * from systems order by system";
        my $sth = $dbh->prepare($query);
                                                                                                                                                             
        $sth->execute();
                                                                                                                                                             
        my $i=0;
        my @systems;
                                                                                                                                                             
        while (my @syshash_ref = $sth->fetchrow_array) {
                $systems[$i] = $syshash_ref[1];
                $i = $i+1;
        }
        if ($sth->err) {
                print "Error: ", $sth->err,"\n";
                exit(0);
        }
                                                                                                                                                             
        return @systems;
}

sub dateForm {

	my $test = $_[0];

	my @years = (getYear()-5,getYear()-4,getYear()-3,getYear()-2,getYear()-1,getYear(),getYear()+1,getYear()+2,getYear()+3,getYear()+4);
	my $downmonth = $session->param('downmonth');
	my $downday = $session->param('downday');
	my $downyear = $session->param('downyear');
	my $downhr = $session->param('downhr');
	my $downmin = $session->param('downmin');
	my $upmonth = $session->param('upmonth');
        my $upday = $session->param('upday');
        my $upyear = $session->param('upyear');
        my $uphr = $session->param('uphr');
        my $upmin = $session->param('upmin');
	
	if (!$downyear && !$upyear){
		$downyear = getYear();
		$upyear = getYear();
	}
	
	if ($test) {
		print	$session->checkbox_group(
                        	-name=>"includeDowntime",
                        	-values=>"Entry added to system after (mm-dd-yyyy): ");
	} else {
		print "<p>Date and time the system was taken down(mm-dd-yyyy hh:mm): ";
	}
        print   $session->popup_menu(
                        -name=>"downmonth",
                        -values=>["01","02","03","04","05","06","07","08","09","10","11","12"],
			-default=>$downmonth),
                "-",
                $session->popup_menu(
                        -name=>"downday",
                        -values=>["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31"],
			-default=>$downday),
                "-",
                $session->popup_menu(
                        -name=>"downyear",
                        -values=>[@years],
			-default=>$downyear);
	
	if (!$test) {
		print	$session->popup_menu(
                        	-name=>"downhr",
                        	-values=>["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23"],
				-default=>$downhr),
                	":",
                	$session->popup_menu(
                	        -name=>"downmin",
                	        -values=>["00","15","30","45"],
				-default=>$downmin),
			"</p>\n<p>Date and time the system was brought back up(mm-dd-yyyy hh:mm):";
	}
	if ($test){
		print	"</p>\n", 
			$session->checkbox_group(
                        -name=>"includeUptime",
                        -values=>"Entry added to system before (mm-dd-yyyy): ");
	}
	
        print	$session->popup_menu(
                        -name=>"upmonth",
                        -values=>["01","02","03","04","05","06","07","08","09","10","11","12"],
			-default=>$upmonth),
                "-",
                $session->popup_menu(
                -name=>"upday",
                        -values=>["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31"],
			-default=>$upday),
                "-",
                $session->popup_menu(
                        -name=>"upyear",
                        -values=>[@years],
			-default=>$upyear);
	if (!$test) {
		print	$session->popup_menu(
                        	-name=>"uphr",
                        	-values=>["00","01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23"],
				-default=>$uphr),
                	":",
                	$session->popup_menu(
                	        -name=>"upmin",
                	        -values=>["00","15","30","45"],
				-default=>$upmin);
	}
}

sub htmlWelcome {

	print<<ENDY;
<h2>Welcome to System Change Manager Please make your selection.</h2>
ENDY
;
}                                                                                                                             

sub htmlAddForm {
	
	my ($error, $subject, $desc, $downmins, $upmins) = @_;

	my %syshash = systemHash();
	my @systems = sysnumArray();
	my @years = (getYear(),getYear()+1,getYear()+2,getYear()+3,getYear()+4);

	if( $error ) {
                print 	'<p class="error">'. $error ."</p>",
        }

	print	"<div id=\"form\">\n",
		"<form name=\"addEntry\" method=\"post\" actions=\"/cgi-bin/pidgeon.cgi\">",
		"<h1>Add New Entry</h1>",
		"<p>System: ",
		$session->popup_menu(
                        -name=>"system",
                        -values=>[@systems],
                        -labels=>\%syshash);
		dateForm();
	print	"</p>\n<p>Summary: ",
		"<input type=\"text\" name=\"subject\" size=\"50\" maxlength=50 value=\"".$subject."\"></p>\n",
		"<p>Description: </p>",
		"<p><textarea name=\"description\" rows=\"20\" cols=\"60\" wrap=virtual>".$desc."</textarea></p>\n",
		"<p><input type=\"submit\" name=\"submitForm\" value=\"Submit\"></p>\n",
		"</form>\n", "</div>\n";
}

sub htmlSearchForm {

	my %syshash = systemHash();
        my @systems = sysnumArray();
	my @years = (getYear()-5,getYear()-4,getYear()-3,getYear()-2,getYear()-1,getYear(),getYear()+1,getYear()+2,getYear()+3,getYear()+4);

	# Start search form
	print 	"<div id=\"form\">\n",
                "<form name=\"search\" method=\"post\" actions=\"/cgi-bin/pidgeon.cgi\">",
		"\n<h1>Search for Entry</h1>",
		"\n<p>",
		$session->checkbox_group(
                        -name=>"includeSystem",
                        -values=>"System: "),
                $session->popup_menu(
                        -name=>"sysname",
                        -values=>[@systems],
                        -labels=>\%syshash),
                "</p>\n<p>Username: ",
                "<input type=\"text\" name=\"searchuid\" maxlength=20></p>",
                "\n<p>";
		dateForm("1");
	print	"</p>\n",
		"<p><input type=\"submit\" name=\"searchForm\" value=\"search\"></p>\n",
                "</form>\n", "</div>\n";
}

sub htmlAddSystem {  # form for adding a new system to the database.

	my $error = $_[0];

	if( $error ) {
                print '<p class="error">'. $error ."</p>\n"
        }

	print 	"<div id=\"form\">\n",
		"<form name=\"addsystem\" method=\"post\" action=\"/cgi-bin/pidgeon.cgi\">\n",
		"<h1>Add a System to the Database</h1>\n",
		"<p><input type=\"text\" name=\"systemAdd\" maxlength=20></p>\n",
		"<p><input type=\"submit\" name=\"addSystemForm\" value=\"Submit\"></p>\n",
		"</form>\n", "</div>\n";		
}

sub htmlFooter {  # create the logout button

	print 	"<br><br><br>\n",
		"<form align=left>\n",
		'<a href="/cgi-bin/pidgeon.cgi?logout=Logout">Logout</a>',
		"</form>\n", "</div>\n";
}

sub addSystem {
	my %syshash=systemHash();
	my @systems=systemArray();
        my $sysString= join(",",@systems);
	my $newSystem = $session->param('systemAdd');
	my $sql;
	
	if ($sysString =~ /$newSystem/i){   # make sure that the system is not already in the database.
                 htmlAddSystem($newSystem." is already in the database.");
	} else {
		$newSystem =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;
		
		if ($database eq "mysql"){
			$sql = "insert into systems (system,username,timestamp) values (\"".$newSystem."\",\"".$session->cookie('uid')."\",now())";
		} else {
			$sql = "insert into systems (sysnum,system,username,timestamp) values (auto_increment.nextval,\'".$newSystem."\',\'".$session->cookie('uid')."\',to_date(\'".currentDate()."\',\'YYYY-MM-DD HH24:MI\'))";
		}

		my $sth = $dbh->prepare($sql);
		$sth->execute;

		print 	"<div id=\"form\">\n",
			"<h2>".$newSystem." has been added to the database.</h2>\n</div>";
	}
}
sub addEntry {
	
	my %syshash = systemHash();
	my @systems = sysnumArray();
	my $system = $session->param('system');
	my $user = $session->cookie('uid');
	my $downtime = join("-",$session->param('downyear'),$session->param('downmonth'),$session->param('downday'))." ".$session->param('downhr').":".$session->param('downmin');
	my $uptime = join("-",$session->param('upyear'),$session->param('upmonth'),$session->param('upday'))." ".$session->param('uphr').":".$session->param('upmin');
	my $subject = $session->param('subject');
	my $desc= $session->param('description');
        my @years=(getYear(),getYear()+1,getYear()+2,getYear()+3,getYear()+4);                                                                                                                                                    
	##### Check and strip html code for security reasons  ####
	$system =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;
	$user =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;
	$subject =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;
	$desc =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;
	##########################################################
        
	# Check to see if the dates are correct.
	my $downmins, my $upmins;
	$downmins = timelocal(0, scalar $session->param('downmin'), scalar $session->param('downhr'), scalar $session->param('downday'), (scalar $session->param('downmonth')) - 1, scalar $session->param('downyear'));
	$upmins = timelocal(0, scalar $session->param('upmin'), scalar $session->param('uphr'), scalar $session->param('upday'), (scalar $session->param('upmonth')) - 1, scalar $session->param('upyear'));

	if ( length $desc < 3800 ){
		if ($upmins > $downmins){
			print	$session->start_form(-method=>"post", -action=>"./pidgeon.cgi"),
				$session->p("System: ",
		                	$session->popup_menu(
	        	                	-name=>"systemSubmit",
	                	        	-values=>[@systems],
	                        		-labels=>\%syshash,
						-default=>$system));
				dateForm();
			print	"</p>\n",
				$session->p("Subject: ", $session->textfield(-name=>"subject", -size=>"50", -default=>$subject)),
				$session->p("Description: "),
				"<p><textarea name=\"description\" rows=\"20\" cols=\"60\" wrap=virtual>".$desc."</textarea></p>\n",
				$session->p("<br><br><br>"),
				$session->p("Check your information. If it is correct, click the submit button. If not change it then click the submit button."),
				$session->submit(
					-name=>"confirmSubmit",
					-value=>"Submit"),
				$session->end_form;
		} else {
			htmlAddForm("The Dates/Times that you entered are not possible. Please change and try again.",$subject,$desc,$downmins,$upmins);
		}
	} else {
		htmlAddForm("The description you entered is too large. Please shorten and resubmit.");
	}
}
	
sub submitEntry {
	my $system = $session->param('systemSubmit');
	my $user = $session->cookie('uid');
	my $subject = $session->param('subject');
	my $desc = $session->param('description');
	my $downtime = join("-",$session->param('downyear'),$session->param('downmonth'),$session->param('downday'))." ".$session->param('downhr').":".$session->param('downmin');
        my $uptime = join("-",$session->param('upyear'),$session->param('upmonth'),$session->param('upday'))." ".$session->param('uphr').":".$session->param('upmin');
        my $sql;                                                                                                                                                    
	$system =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;
	$user =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;
	$subject =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;
	$desc =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;

	$subject = $dbh->quote($subject);
	$desc = $dbh->quote($desc);

	my $downmins, my $upmins;
        $downmins = timelocal(0, scalar $session->param('downmin'), scalar $session->param('downhr'), scalar $session->param('downday'), (scalar $session->param('downmonth')) - 1, scalar $session->param('downyear'));
        $upmins = timelocal(0, scalar $session->param('upmin'), scalar $session->param('uphr'), scalar $session->param('upday'), (scalar $session->param('upmonth')) - 1, scalar $session->param('upyear'));

	if ($upmins > $downmins){
                                                                                                                                                            
		if ($database eq "mysql"){
			$sql = "insert into actions (system,username,downtime,uptime,subject,action,timestamp) values (\"".join("\",\"",$system,$user,$downtime,$uptime)."\",".$subject.",".$desc.",now())";
		} else {
#			my $check = $dbh->get_info(14);
#			$subject =~ s/(\'|\[|\]|\(|\))/$check$1/g;
#			$desc =~ s/(\'|\[|\]|\(|\))/$check$1/g;
			$sql = "insert into actions (system,username,downtime,uptime,subject,action,timestamp,entryid) values ('".$system."','".$user."',to_date('".$downtime."','YYYY-MM-DD HH24:MI')".",to_date('".$uptime."','YYYY-MM-DD HH24:MI'),".$subject.",".$desc.",to_date('".currentDate()."','YYYY-MM-DD HH24:MI'),entryid.nextval)";
		}
                                                                                                                                                            
		my $sth = $dbh->prepare($sql);
                                                                                                                                                            
		$sth->execute;
                                                                                                                                                            
		print	"<div id=\"form\">\n",
			"<h2>The new entry has been added.</h2>\n</div>";
	} else {
		htmlAddForm("The Dates/Times that you entered are not possible. Please change and try again.",$subject,$desc,$downmins,$upmins);
	}
}

sub displaySearch {

	my $selections, my $srchstrng, my $i, my $numcols, my $color;
	my @tmp, my @row;
	my %syshash = systemHash();

	# Figure out what the user wants to display

	$selections = 'select systems.system, actions.username,actions.subject,actions.entryid from actions, systems where actions.system=systems.sysnum';
	
	# Append what the user is searching for to the search string.

	my $system=$syshash{$session->param('sysname')};
	my $user=$session->param('searchuid');
	my $aftertime = join("-",$session->param('downyear'),$session->param('downmonth'),$session->param('downday'));
	my $beforetime = join("-",$session->param('upyear'),$session->param('upmonth'),$session->param('upday'));
        
	$user =~ s/<(?:[^>'"]*|(['"])­.*?\1)*>//gs;  # error check user since it is the only free entry from in the search form.

	if ($session->param('includeSystem')){
		$srchstrng .= " and systems.system='".$system."'";
	}
	if ($user){
		$srchstrng .= " and actions.user='".$user."'";
	}
	if ($beforetime && $session->param('includeUptime')){
		if ($database eq "mysql"){
			$srchstrng .= " and actions.timestamp<'".$beforetime."'";
		} else {
			$srchstrng .= " and actions.timestamp<to_date('".$beforetime."','YYYY-MM-DD')";
		}
	}
	if ($aftertime && $session->param('includeDowntime')){
		if ($database eq "mysql"){
                        $srchstrng .= " and actions.timestamp>'".$aftertime."'";
                } else {
			$srchstrng .= " and actions.timestamp>to_date('".$aftertime."','YYYY-MM-DD')";
		}
	}

	#start display

	my $query =$selections.$srchstrng;
                                                                                                                                                             
	my $sth = $dbh->prepare($query);
	$sth->execute();
                                                                                                                                                             
	@tmp = ("Username","Subject");
        
	$numcols = $#tmp;

	print "<table border=1 width=100%>\n";
        print "<tr>\n";
        print "<th>System</th>\n";
        for ($i = 0; $i<=$numcols; $i++){
                print "<th>".@tmp[$i]."</th>\n";
        }

	while (@row=$sth->fetchrow_array){
		if ($color eq "#B8B8B8") {
                        $color = "#FFFFFF";
                } else {
                        $color = "#B8B8B8";
                }
                print "<tr>\n";
		print "<td bgcolor=\"$color\"><a href=pidgeon.cgi?entryid=".$row[$numcols+2]." target=\"_blank\">".$row[0]."</a></td>\n";
                for ($i = 1; $i<=$numcols+1; $i++){
                        print "<td bgcolor=\"$color\">".$row[$i]."</td>\n";
                }
                print 	"</tr>\n";
        }

	print 	"</table>\n",
                "<br>\n";
}

sub display_details {

	my $entryid=$session->param('entryid'), my @row, my $i;

	my $selection= "select systems.system, actions.username,actions.downtime,actions.uptime,actions.subject,actions.action from actions, systems where actions.system=systems.sysnum and actions.entryid=".$entryid;

	my $sth = $dbh->prepare($selection);
        $sth->execute();

	my @tmp = ("Username","Downtime","Uptime","Subject","Description");

	my $numcols = $#tmp;

	@row = $sth->fetchrow_array;

        print   "<table border=1 width=100%>\n";
        print   "<tr>\n";
        print   "<th>System</th>\n";
        for ($i = 0; $i<$numcols; $i++){
                print "<th>".@tmp[$i]."</th>\n";
        }
        print "</tr>\n<tr>\n";
        for ($i = 0; $i<=$numcols; $i++){
                print "<td>".$row[$i]."</td>\n";
        }
        print   "</tr>\n";
        print   "<tr>\n",
                "<th colspan=\"5\">".$tmp[$numcols]."</th>\n",
                "</tr>\n<tr>\n",
                "<td colspan=\"5\">".$row[$numcols+1]."</td>\n",
                "</tr>\n",
                "</table>\n",
                "<br>\n";
}

if ($session->param('login') || $session->cookie('login')) {
	my $uid, my $pass;
	# handle login for
	
	if ($session->cookie('login')){
		$uid = $session->cookie('uid');
		$pass = $session->cookie('pass');
	} else {
		$uid = $session->param('uid');
		$pass = $session->param('pass');
	}

	if( $uid eq "" ) {
		htmlHeader( "Please enter your username and password." );
		htmlLogin();
	} elsif( $pass eq "" ) {
		htmlHeader( "Please enter your password." );
		htmlLogin( $uid );
	} elsif ($uid && $pass){
		my $result = LDAPLogin( $uid, $pass );

		# decipher the ldap codes
		if( $result->code == 32 ) {
			htmlHeader( "User does not exist." );
			htmlLogin();
		} elsif( $result->code == 49 ) {
			htmlHeader( "Password is incorrect." );
			htmlLogin( $uid );
		} else {
			if ($session->param('submitForm')){
				htmlHeader();
				htmlFrame();
                                htmlMenu();
				addEntry();
				htmlEndTable();
			} elsif ($session->param('confirmSubmit')){
				htmlHeader();
				htmlFrame();
                                htmlMenu();
				submitEntry();
				htmlEndTable();
			} elsif ($session->param('searchForm')){
				htmlHeader();
				htmlFrame();
                                htmlMenu();
				displaySearch();
				htmlEndTable();
			} elsif ($session->param('addSystemForm')){
				htmlHeader();
                                htmlFrame();
                                htmlMenu();
				addSystem();
				htmlEndTable();
			} elsif ($session->param('addSystem')){
				htmlHeader();
                                htmlFrame();
                                htmlMenu();
				htmlAddSystem();
				htmlEndTable();
			} elsif ($session->param('logout')){
				htmlHeader();
				htmlLogin();
			} elsif ($session->param('search')){
				htmlHeader();
				htmlFrame();
                                htmlMenu();
				htmlSearchForm();
				htmlEndTable();
			} elsif ($session->param('add')){
				htmlHeader();
				htmlFrame();
                                htmlMenu();
				htmlAddForm();
				htmlEndTable();
			} elsif ($session->param('entryid')){
				htmlHeader();
				htmlFrame();
				htmlMenu();
				display_details();
				htmlEndTable();
			} else{
				htmlHeader();
				htmlFrame();
				htmlMenu();
				htmlWelcome();
				htmlEndTable();
			}
		}
	}
} else {
	# Show default login page.
	htmlHeader();
	htmlLogin();
}
