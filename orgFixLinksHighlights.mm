<map version="freeplane 1.3.0">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="orgFixLinks project" ID="ID_1723255651" CREATED="1283093380553" MODIFIED="1482604082027"><hook NAME="MapStyle">

<map_styles>
<stylenode LOCALIZED_TEXT="styles.root_node">
<stylenode LOCALIZED_TEXT="styles.predefined" POSITION="right">
<stylenode LOCALIZED_TEXT="default" MAX_WIDTH="600" COLOR="#000000" STYLE="as_parent">
<font NAME="SansSerif" SIZE="10" BOLD="false" ITALIC="false"/>
</stylenode>
<stylenode LOCALIZED_TEXT="defaultstyle.details"/>
<stylenode LOCALIZED_TEXT="defaultstyle.note"/>
<stylenode LOCALIZED_TEXT="defaultstyle.floating">
<edge STYLE="hide_edge"/>
<cloud COLOR="#f0f0f0" SHAPE="ROUND_RECT"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.user-defined" POSITION="right">
<stylenode LOCALIZED_TEXT="styles.topic" COLOR="#18898b" STYLE="fork">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.subtopic" COLOR="#cc3300" STYLE="fork">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.subsubtopic" COLOR="#669900">
<font NAME="Liberation Sans" SIZE="10" BOLD="true"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.important">
<icon BUILTIN="yes"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.AutomaticLayout" POSITION="right">
<stylenode LOCALIZED_TEXT="AutomaticLayout.level.root" COLOR="#000000">
<font SIZE="18"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,1" COLOR="#0033ff">
<font SIZE="16"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,2" COLOR="#00b439">
<font SIZE="14"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,3" COLOR="#990000">
<font SIZE="12"/>
</stylenode>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,4" COLOR="#111111">
<font SIZE="10"/>
</stylenode>
</stylenode>
</stylenode>
</map_styles>
</hook>
<hook NAME="AutomaticEdgeColor" COUNTER="4"/>
<node TEXT="local vs global variables" POSITION="right" ID="ID_429026029" CREATED="1482611810804" MODIFIED="1482611821065">
<edge COLOR="#7c0000"/>
<node TEXT="struggling with how to do the database" ID="ID_1947211914" CREATED="1482611832043" MODIFIED="1482611841634">
<node TEXT="chose a global variable; clumsy" ID="ID_406606979" CREATED="1482611843115" MODIFIED="1482611848586"/>
</node>
</node>
<node TEXT="object oriented code" POSITION="right" ID="ID_1952916038" CREATED="1482605765061" MODIFIED="1482605769148">
<edge COLOR="#ff0000"/>
<node TEXT="seems non-optional in this project" ID="ID_110919543" CREATED="1482605774653" MODIFIED="1482605785639"/>
</node>
<node TEXT="ipython" POSITION="right" ID="ID_1704135118" CREATED="1482605426839" MODIFIED="1482605428982">
<edge COLOR="#007c7c"/>
<node TEXT="reviewed my notes on it, but never seem to learn/memorize anything beyond tab completion" ID="ID_428615165" CREATED="1482605436992" MODIFIED="1482605459199"/>
<node TEXT="cpaste" ID="ID_1392636857" CREATED="1482605464647" MODIFIED="1482605466325"/>
<node TEXT="manually copying ipython stuff into an org file" ID="ID_132998223" CREATED="1482605472767" MODIFIED="1482605487061">
<node TEXT="e.g. developing regex" ID="ID_8501699" CREATED="1482605488567" MODIFIED="1482605497529"/>
<node TEXT="this is a dud; org file gets too long" ID="ID_1465723716" CREATED="1482605497895" MODIFIED="1482605503497"/>
<node TEXT="better to put that stuff in a separate file and link to it in org file" ID="ID_176345360" CREATED="1482605504246" MODIFIED="1482605519941"/>
<node TEXT="unittest essential" ID="ID_459751239" CREATED="1482605525582" MODIFIED="1482605541381"/>
</node>
</node>
<node TEXT="error handling" POSITION="right" ID="ID_348616911" CREATED="1482612639438" MODIFIED="1482612641956">
<edge COLOR="#ff0000"/>
<node TEXT="how to keep spidering despite errors" ID="ID_125084557" CREATED="1482612650166" MODIFIED="1482612663820"/>
</node>
<node TEXT="debugging" POSITION="right" ID="ID_510624898" CREATED="1482611673901" MODIFIED="1482611676282">
<edge COLOR="#ffff00"/>
<node TEXT="sweigart automate the boring stuff textbook" ID="ID_845450460" CREATED="1482611728148" MODIFIED="1483572067452"/>
<node TEXT="logging in python" ID="ID_922102371" CREATED="1482611531654" MODIFIED="1482611684415">
<node TEXT="log file including DEBUG statements can get much too large and unreadable" ID="ID_213432298" CREATED="1482611564822" MODIFIED="1482611581780"/>
<node TEXT="log file can be useful for debugging" ID="ID_521686225" CREATED="1482611583605" MODIFIED="1482611596547"/>
<node TEXT="cat logfile | grep &apos;ERROR&apos; | grep -i &apos;an error happened&apos; | less" ID="ID_1338645611" CREATED="1482611600485" MODIFIED="1482611635435">
<node TEXT="or something like this" ID="ID_341442138" CREATED="1482611637229" MODIFIED="1482611641195"/>
</node>
<node TEXT="turn off logging temporarily" ID="ID_1305533971" CREATED="1482612824421" MODIFIED="1482612840666">
<node TEXT="when analyzing a file in a link in a header" ID="ID_1040878538" CREATED="1482612842156" MODIFIED="1482612858714"/>
<node TEXT="did not achieve this?" ID="ID_1046907929" CREATED="1482612859228" MODIFIED="1482612870139"/>
</node>
<node TEXT="upon completion, script reports how many errors and warnings are in the log file" ID="ID_1050994688" CREATED="1482613327921" MODIFIED="1482613344302"/>
</node>
<node TEXT="pudb" ID="ID_43432548" CREATED="1482611689541" MODIFIED="1482611693251">
<node TEXT="just insert pudb.set_trace() in any code at the right place" ID="ID_1989248484" CREATED="1482611697176" MODIFIED="1482611710315"/>
<node TEXT="once code gets thousands of lines long, stepping line by line in pudb can be tough" ID="ID_1325624628" CREATED="1482612292636" MODIFIED="1482612308110"/>
</node>
<node TEXT="assert statement" ID="ID_847156512" CREATED="1482611716364" MODIFIED="1482611719499">
<node TEXT="used tons and tons of these" ID="ID_623205423" CREATED="1482611743637" MODIFIED="1482611749115"/>
</node>
<node TEXT="pretty graphical tool to look at a diff of two files" ID="ID_1366704246" CREATED="1482612347426" MODIFIED="1482612361110">
<node TEXT="meld" ID="ID_498354186" CREATED="1482612362487" MODIFIED="1482612363574"/>
</node>
<node TEXT="unittest" ID="ID_656689072" CREATED="1482604064362" MODIFIED="1482612539453">
<icon BUILTIN="password"/>
<node TEXT="drastically useful for this project" ID="ID_281850951" CREATED="1482604283528" MODIFIED="1482604305886"/>
<node TEXT="must write test before writing code; much easier" ID="ID_1862760268" CREATED="1482604311664" MODIFIED="1482604329662"/>
<node TEXT="can execute just a single test via command line" ID="ID_663735167" CREATED="1482604356719" MODIFIED="1482604391574">
<node TEXT="great for writing and debugging that one test" ID="ID_891190501" CREATED="1482604393231" MODIFIED="1482604411566"/>
</node>
</node>
<node TEXT="simple test files that link to each other" ID="ID_897768905" CREATED="1482612598286" MODIFIED="1482612608627">
<node TEXT="test script creates them, operates on them, finally deletes them" ID="ID_555089453" CREATED="1482612621086" MODIFIED="1482612633180"/>
</node>
</node>
<node TEXT="why orgFixLinks.py?" POSITION="left" ID="ID_207969756" CREATED="1482612959364" MODIFIED="1483571990108">
<edge COLOR="#0000ff"/>
<node TEXT="idea came from twitter scraper in severance python for informatics textbook" ID="ID_1204900561" CREATED="1482604684677" MODIFIED="1483570225927"/>
<node TEXT="broken links in my org files are a pain" ID="ID_921133748" CREATED="1482612967724" MODIFIED="1482612979594">
<node TEXT="workflow getting seriously derailed by broken links" ID="ID_983864292" CREATED="1482612981403" MODIFIED="1483570257407"/>
</node>
<node TEXT="why this .mm file?" ID="ID_772314701" CREATED="1482614277202" MODIFIED="1482614286825">
<node TEXT="why describe an org project with a .mm file?" ID="ID_1454037927" CREATED="1482614288730" MODIFIED="1482614298384"/>
<node TEXT="I like looking at this entire file at once on a 27&quot; monitor" ID="ID_1273082019" CREATED="1482614298890" MODIFIED="1482614319505"/>
<node TEXT="there is a large org file about this project, but it is not fit for public consumption" ID="ID_846662668" CREATED="1482614323921" MODIFIED="1482614337792"/>
<node TEXT="I like writing in org, but I prefer reading in freeplane" ID="ID_67614436" CREATED="1482614350785" MODIFIED="1482614359516"/>
</node>
<node TEXT="wanted python practice vs just reading textbooks" ID="ID_1020555300" CREATED="1483571986963" MODIFIED="1483572009921"/>
<node TEXT="why is it on github?" ID="ID_292616561" CREATED="1483571453399" MODIFIED="1483571459934">
<node TEXT="would like to see it used and improved by others" ID="ID_43869815" CREATED="1483571467959" MODIFIED="1483571483901"/>
</node>
</node>
<node TEXT="links in an org file" POSITION="left" ID="ID_1951756195" CREATED="1482611984971" MODIFIED="1483571506157">
<edge COLOR="#7c007c"/>
<node TEXT="types of links in org mode" ID="ID_1332298568" CREATED="1482604434303" MODIFIED="1482611992578">
<node TEXT="http://orgmode.org/manual/Hyperlinks.html#Hyperlinks" ID="ID_1808015695" CREATED="1482605116394" MODIFIED="1482605116394" LINK="http://orgmode.org/manual/Hyperlinks.html#Hyperlinks">
<node TEXT="internal link to a &lt;&lt;dedicated target&gt;&gt;" ID="ID_336750304" CREATED="1482604440975" MODIFIED="1482604455784"/>
</node>
<node TEXT="create an org file where you simply type in various links and observe how org treats them" ID="ID_658117180" CREATED="1482613035978" MODIFIED="1483570339246"/>
</node>
<node TEXT="regular expressions" ID="ID_676257880" CREATED="1482604092682" MODIFIED="1482611995660">
<node TEXT="identify what text is a link" ID="ID_337750831" CREATED="1482604105153" MODIFIED="1482604119168">
<node TEXT="brackets vs no brackets" ID="ID_79241380" CREATED="1482604133809" MODIFIED="1482604137816"/>
<node TEXT="unittest is essential for this" ID="ID_1843199250" CREATED="1482605334201" MODIFIED="1482605340503"/>
<node TEXT="ipython" ID="ID_58111615" CREATED="1482605377456" MODIFIED="1482605380150"/>
<node TEXT="regex101.com" ID="ID_318948036" CREATED="1482605380863" MODIFIED="1482605383966">
<node TEXT="choose python mode" ID="ID_1792120196" CREATED="1482605387631" MODIFIED="1482605390606"/>
</node>
</node>
</node>
<node TEXT="symlinks" ID="ID_1024217291" CREATED="1482604463246" MODIFIED="1482611998205">
<node TEXT="os.path.islink" ID="ID_903919132" CREATED="1482604984362" MODIFIED="1482604987785"/>
<node TEXT="os.symlink" ID="ID_1092730899" CREATED="1482604964843" MODIFIED="1482611096199">
<node TEXT="create a symlink in python" ID="ID_693864156" CREATED="1482611050113" MODIFIED="1482611071863"/>
</node>
<node TEXT="to make things simpler, all links to symlinks in an org file are replaced with targets of those symlinks" ID="ID_438415378" CREATED="1483570472390" MODIFIED="1483570508765">
<node TEXT="commit 8b4d61931fa8359a50466d7a69ef40758daee4e4" ID="ID_947248011" CREATED="1483570518350" MODIFIED="1483570556028"/>
</node>
</node>
<node TEXT="schemes for repairing broken links" ID="ID_21008570" CREATED="1482611003666" MODIFIED="1482612014051">
<node TEXT="org file" ID="ID_1442514116" CREATED="1482611018916" MODIFIED="1482611020727"/>
<node TEXT="non-org file" ID="ID_274423055" CREATED="1482611021393" MODIFIED="1482611023594"/>
<node TEXT="max number of repair attempts" ID="ID_653830421" CREATED="1482612430968" MODIFIED="1482612435701"/>
<node TEXT="interactive repair of links in the terminal" ID="ID_1996961196" CREATED="1482612468217" MODIFIED="1482612481843">
<node TEXT="use a csv file to store user repairs" ID="ID_1045311194" CREATED="1482612487719" MODIFIED="1482612498629"/>
<node TEXT="menu-driven" ID="ID_1314648919" CREATED="1482612769545" MODIFIED="1482612771851"/>
</node>
<node TEXT="calling bash via python to find files by name" ID="ID_1858666918" CREATED="1482611160776" MODIFIED="1482614544842"/>
<node TEXT="various schemes are methods of classes LinkToLocalFile, LinkToOrgFile" ID="ID_1522910179" CREATED="1483570695328" MODIFIED="1483570720955"/>
</node>
<node TEXT="blacklisting for link repair" ID="ID_1380965128" CREATED="1483571669941" MODIFIED="1483571679213">
<node TEXT="which broken links to not repair" ID="ID_495769597" CREATED="1483571687133" MODIFIED="1483571693844"/>
<node TEXT="which files to not use for link repair" ID="ID_260278642" CREATED="1483571694245" MODIFIED="1483571711164"/>
<node TEXT="list of folder names that cannot be in an absolute path filename" ID="ID_656756569" CREATED="1483571035426" MODIFIED="1483571058753">
<node TEXT="e.g. &apos;venv&apos; in &apos;/home/username/venv/filename.ext&apos;" ID="ID_514166573" CREATED="1483571061434" MODIFIED="1483571076960"/>
<node TEXT="blacklisted foldernames (e.g. &apos;venv&apos;) do not have to exist on disk" ID="ID_648985959" CREATED="1483571169545" MODIFIED="1483571189248"/>
</node>
<node TEXT="config file .OFLDoNotRepairLink" ID="ID_736133067" CREATED="1483571084841" MODIFIED="1483571891394">
<node TEXT="each line is interpreted using glob.glob to match one or more files or folders on disk; these matches are blacklisted from being spidered" ID="ID_234569151" CREATED="1483571104314" MODIFIED="1483571142954">
<node TEXT="matches must exist on disk" ID="ID_584644905" CREATED="1483571199729" MODIFIED="1483571206626"/>
</node>
</node>
</node>
</node>
<node TEXT="why the &apos;machine-generated header&apos;?" POSITION="left" ID="ID_1603552209" CREATED="1482614420794" MODIFIED="1482614498903">
<edge COLOR="#00ff00"/>
<node TEXT="a redundant storage of unique IDs, in addition to the sqlite database" ID="ID_393230148" CREATED="1482614431848" MODIFIED="1482614454655"/>
<node TEXT="I find this index of links and tags to be useful" ID="ID_80153451" CREATED="1482614455856" MODIFIED="1483570763493"/>
<node TEXT="default script behavior: header is not added to files.  enabled via command line option." ID="ID_758415539" CREATED="1483570769236" MODIFIED="1483570807435"/>
</node>
<node TEXT="a unique identifier inside each org file" POSITION="left" ID="ID_1664576126" CREATED="1482604824460" MODIFIED="1482604833690">
<edge COLOR="#007c00"/>
<node TEXT="simple-minded scheme" ID="ID_523151648" CREATED="1482604863163" MODIFIED="1482604867707">
<node TEXT="git approach is likely superior in every way?" ID="ID_637773300" CREATED="1482604847020" MODIFIED="1483570859381"/>
</node>
<node TEXT="file can be moved/renamed, but can still be identified based on unique ID inside it" ID="ID_1714340020" CREATED="1482614727111" MODIFIED="1482614746324"/>
</node>
<node TEXT="a hash of a file" POSITION="left" ID="ID_1436666956" CREATED="1482605657318" MODIFIED="1482605662460">
<edge COLOR="#7c7c00"/>
<node TEXT="used this in unittest script to tell if a file contents are the same or have changed" ID="ID_155447952" CREATED="1482605667486" MODIFIED="1482605691216"/>
</node>
<node TEXT="rewriting the script so it can be imported as a module in the test script" POSITION="right" ID="ID_1607943089" CREATED="1482611924410" MODIFIED="1482611934820">
<edge COLOR="#007c00"/>
<node TEXT="if __name__==&quot;__main__&quot;" ID="ID_490309984" CREATED="1482611854523" MODIFIED="1482611942981">
<node TEXT="using a main function i.e. def main()" ID="ID_1840812680" CREATED="1482611897019" MODIFIED="1482611913113"/>
</node>
</node>
<node TEXT="git and github" POSITION="right" ID="ID_475864385" CREATED="1482604541550" MODIFIED="1482604544621">
<edge COLOR="#ffff00"/>
<node TEXT="basic operation is pretty easy once you do it awhile" ID="ID_1405797116" CREATED="1482604553510" MODIFIED="1482604574701"/>
<node TEXT="free online textbook pro git; mainly chapter 2" ID="ID_1250218297" CREATED="1482605044107" MODIFIED="1482614904670"/>
<node TEXT="useful git commands" ID="ID_1953638116" CREATED="1482605024099" MODIFIED="1482605027872">
<node TEXT="git status" ID="ID_1766665975" CREATED="1482604591654" MODIFIED="1482604598252"/>
<node TEXT="git add ." ID="ID_748776110" CREATED="1482604600182" MODIFIED="1482604606572"/>
<node TEXT="git commit -m &apos;a message&apos;" ID="ID_1071142246" CREATED="1482604608733" MODIFIED="1482604614932"/>
<node TEXT="git remote -v" ID="ID_1086436810" CREATED="1482604620189" MODIFIED="1482604632468"/>
<node TEXT="git push remoteName master" ID="ID_528988021" CREATED="1482604636957" MODIFIED="1482604643628"/>
</node>
<node TEXT="github wiki" ID="ID_1560932080" CREATED="1482605562008" MODIFIED="1482605564900">
<node TEXT="working on wiki pages locally in emacs" ID="ID_954261347" CREATED="1482605566254" MODIFIED="1482605577629">
<node TEXT="markdown language" ID="ID_133535323" CREATED="1482605601950" MODIFIED="1482605607173"/>
<node TEXT="had to write python script to convert files back and forth due to differing link format" ID="ID_1540266140" CREATED="1482605578791" MODIFIED="1482605598845">
<node TEXT="https://github.com/cashTangoTangoCash/convertLinksGithubWikiEmacs" ID="ID_1359321660" CREATED="1482613169978" MODIFIED="1482613199620" LINK="https://github.com/cashTangoTangoCash/convertLinksGithubWikiEmacs"/>
</node>
<node TEXT="this is pretty quick and easy once you get going" ID="ID_1092131835" CREATED="1482605611702" MODIFIED="1482605618784"/>
</node>
</node>
</node>
<node TEXT="worg" POSITION="right" ID="ID_1013388168" CREATED="1482604648220" MODIFIED="1482604654356">
<edge COLOR="#7c0000"/>
<node TEXT="ssh keys" ID="ID_1002658536" CREATED="1482604656309" MODIFIED="1482604659411">
<node TEXT="worg has a very good tutorial on this" ID="ID_921911534" CREATED="1482611648252" MODIFIED="1482611659555"/>
</node>
<node TEXT="uses git to allow multiple contributors" ID="ID_1227062581" CREATED="1482613253922" MODIFIED="1483572149873"/>
</node>
<node TEXT="contributing to this project" POSITION="right" ID="ID_1695709971" CREATED="1483571268632" MODIFIED="1483571274336">
<edge COLOR="#ff00ff"/>
<node TEXT="code seems long and complicated; needs real use in order to reveal bugs" ID="ID_105284819" CREATED="1483572365568" MODIFIED="1483572393430">
<node TEXT="tests were written, but do not cover everything" ID="ID_1579046639" CREATED="1483572399376" MODIFIED="1483572415271"/>
</node>
<node TEXT="this project would benefit from multiple developers" ID="ID_1372866316" CREATED="1483571281015" MODIFIED="1483571421982">
<node TEXT="no one person is going to have files on disk that will exhibit all bugs" ID="ID_593438049" CREATED="1483571296828" MODIFIED="1483571318462"/>
<node TEXT="too much work for a single developer to remotely figure out bugs of users?" ID="ID_688532839" CREATED="1483571322375" MODIFIED="1483571404534">
<node TEXT="much easier to be on the computer where bug is appearing" ID="ID_1902062801" CREATED="1483571356111" MODIFIED="1483571386422"/>
</node>
</node>
<node TEXT="make it better match every different feature of an org file" ID="ID_293693699" CREATED="1483572599767" MODIFIED="1483572622492">
<node TEXT="existing script is likely unaware of some features, and may trample over them" ID="ID_1525927214" CREATED="1483572625294" MODIFIED="1483572646001"/>
</node>
<node TEXT="keep up with changes in org mode" ID="ID_707266153" CREATED="1483572654462" MODIFIED="1483572663573"/>
<node TEXT="someone port it to Windows/Mac; I don&apos;t plan to do this" ID="ID_1620664867" CREATED="1483572245393" MODIFIED="1483572262086"/>
<node TEXT="needs to be revised for Python 3 since Python 2 will no longer be supported" ID="ID_1058339762" CREATED="1483572265961" MODIFIED="1483572289371"/>
</node>
<node TEXT="spidering files" POSITION="left" ID="ID_994080656" CREATED="1482611391855" MODIFIED="1482611395288">
<edge COLOR="#ff00ff"/>
<node TEXT="in this script, spidering means: finding the outgoing links to org files inside an org file, then recursively doing the same with the org files linked to" ID="ID_1177686242" CREATED="1483570941427" MODIFIED="1483571009953"/>
<node TEXT="settings to blacklist files from being spidered" ID="ID_1772227072" CREATED="1483570893179" MODIFIED="1483570924290">
<node TEXT="list of folder names that cannot be in an absolute path filename" ID="ID_157403924" CREATED="1483571035426" MODIFIED="1483571058753">
<node TEXT="e.g. &apos;venv&apos; in &apos;/home/username/venv/filename.ext&apos;" ID="ID_1557679135" CREATED="1483571061434" MODIFIED="1483571076960"/>
<node TEXT="blacklisted foldernames (e.g. &apos;venv&apos;) do not have to exist on disk" ID="ID_691583218" CREATED="1483571169545" MODIFIED="1483571189248"/>
</node>
<node TEXT="config file .OFLDoNotSpider" ID="ID_616895891" CREATED="1483571084841" MODIFIED="1483571091939">
<node TEXT="each line is interpreted using glob.glob to match one or more files or folders on disk; these matches are blacklisted from being spidered" ID="ID_1818222191" CREATED="1483571104314" MODIFIED="1483571142954">
<node TEXT="matches must exist on disk" ID="ID_1179845086" CREATED="1483571199729" MODIFIED="1483571206626"/>
</node>
</node>
</node>
<node TEXT="speed things up by looking up outgoing links of an org file in database" ID="ID_680747940" CREATED="1482611396966" MODIFIED="1482611411509">
<node TEXT="rather than analyzing file" ID="ID_74048298" CREATED="1482611412942" MODIFIED="1482611418647"/>
</node>
<node TEXT="user can hit any key to stop spidering" ID="ID_1151355617" CREATED="1482612049026" MODIFIED="1482612742808">
<node TEXT="problem: interactive repair of links is also looking for keyboard input from user" ID="ID_1535564910" CREATED="1482612087497" MODIFIED="1482612103498"/>
<node TEXT="solution: threading module" ID="ID_64109591" CREATED="1482612079362" MODIFIED="1482612112944"/>
</node>
</node>
<node TEXT="sqlite database" POSITION="left" ID="ID_1797106018" CREATED="1482604916195" MODIFIED="1482604920433">
<edge COLOR="#7c007c"/>
<node TEXT="why?" ID="ID_1411586596" CREATED="1483571523214" MODIFIED="1483571525557">
<node TEXT="I never did it before, and this project seemed like a good chance to try it" ID="ID_98967710" CREATED="1483571532438" MODIFIED="1483571556333"/>
<node TEXT="seems like using a database to add a memory to this script would allow it to fix more links, more quickly" ID="ID_1532214535" CREATED="1483571563445" MODIFIED="1483571586261"/>
</node>
<node TEXT="adding a database to this code drastically slowed down writing the code, and increased the complexity" ID="ID_945220435" CREATED="1482611765595" MODIFIED="1483571626364"/>
<node TEXT="zetcode material is enough" ID="ID_1400408955" CREATED="1482605068554" MODIFIED="1482605073008"/>
<node TEXT="command line tool" ID="ID_1744930796" CREATED="1482611223392" MODIFIED="1482611236765">
<node TEXT="not very user-friendly" ID="ID_1669068085" CREATED="1482611238271" MODIFIED="1482611242062"/>
<node TEXT="never got tab completion working" ID="ID_217249542" CREATED="1482611242384" MODIFIED="1482611247062"/>
<node TEXT="integers instead of strings makes printout in terminal less informative" ID="ID_322020146" CREATED="1482611255464" MODIFIED="1482611276592">
<node TEXT="foreign keys" ID="ID_231488056" CREATED="1482611277904" MODIFIED="1482611281497"/>
</node>
</node>
<node TEXT="default python interface to database seems less intuitive" ID="ID_1623196176" CREATED="1482611453238" MODIFIED="1482611478556">
<node TEXT="I end up writing lots of wrappers" ID="ID_3766817" CREATED="1482611483237" MODIFIED="1482611491190"/>
</node>
</node>
<node TEXT="dry run mode" POSITION="left" ID="ID_946641290" CREATED="1482612138682" MODIFIED="1482612143887">
<edge COLOR="#7c7c00"/>
<node TEXT="dry run database vs real database" ID="ID_1639780507" CREATED="1482612152369" MODIFIED="1482612158000">
<node TEXT="only write to real database when run is a success" ID="ID_853758239" CREATED="1482612251089" MODIFIED="1482612270926"/>
</node>
<node TEXT="dry run mode does not revise org files on disk" ID="ID_1728969121" CREATED="1482612162841" MODIFIED="1482612174848">
<node TEXT="leads to assert statements halting run when database says there should be unique ID in a file, but file does not contain one" ID="ID_1678820314" CREATED="1482612176520" MODIFIED="1482612213065"/>
</node>
</node>
</node>
</map>
