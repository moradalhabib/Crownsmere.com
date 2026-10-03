#!/usr/local/bin/php -q
<?php
/**
 * Crownsmere Estate — daily digest of filtered mail
 *
 * Run once a day from a cPanel cron job. Emails Alaa a short list of the
 * messages the filter held back in the last 24 hours (sender, subject and the
 * reason), so anything misjudged can be found in the hello@ mailbox.
 * Sends nothing on days when nothing was filtered.
 *
 * Usage (testing):  php digest.php --dry-run
 */

declare(strict_types=1);

$dryRun = in_array('--dry-run', $argv ?? [], true);
$config = require __DIR__ . '/config.php';

if (empty($config['daily_digest']) || str_contains($config['forward_to'], 'PRIVATE-ADDRESS')) {
    exit(0);
}

$since = time() - 24 * 3600;
$held = [];
$forwarded = 0;

$fh = @fopen($config['log_file'], 'r');
if ($fh !== false) {
    while (($line = fgets($fh)) !== false) {
        $entry = json_decode($line, true);
        if (!is_array($entry) || strtotime($entry['time'] ?? '') < $since) {
            continue;
        }
        if (($entry['event'] ?? '') === 'discarded') {
            $held[] = $entry;
        } elseif (($entry['event'] ?? '') === 'forwarded') {
            $forwarded++;
        }
    }
    fclose($fh);
}

if (!$held) {
    if ($dryRun) {
        fwrite(STDERR, "Nothing filtered in the last 24 hours: no digest sent.\n");
    }
    exit(0);
}

$lines = [];
foreach ($held as $e) {
    $when = date('D H:i', strtotime($e['time']));
    $lines[] = "{$when}  {$e['from']}\n        {$e['subject']}\n        Why: {$e['reason']}";
}

$count = count($held);
$body = "Good morning,\n\n"
    . "In the last 24 hours the inbox filter forwarded {$forwarded} email" . ($forwarded === 1 ? '' : 's')
    . " to you and held back {$count}:\n\n"
    . implode("\n\n", $lines) . "\n\n"
    . "Every one of these is still in the hello@ mailbox (Webmail). If anything here should have reached you, "
    . "open it there, and add the sender to 'always_forward' in config.php so it comes straight through next time.\n";

$subject = "Inbox filter: {$count} email" . ($count === 1 ? '' : 's') . ' held back today';
$headers = implode("\r\n", [
    'From: ' . $config['forward_from_name'] . ' <' . $config['forward_from'] . '>',
    'To: ' . $config['forward_to'],
    'Subject: ' . $subject,
    'Date: ' . date(DATE_RFC2822),
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'X-Crownsmere-Filter: digest',
    'Auto-Submitted: auto-generated',
]);
$message = $headers . "\r\n\r\n" . str_replace("\n", "\r\n", $body);

if ($dryRun) {
    fwrite(STDERR, $message . "\n");
    exit(0);
}

$pipe = popen(escapeshellcmd($config['sendmail_path']) . ' -t -i -f ' . escapeshellarg($config['forward_from']), 'w');
if ($pipe !== false) {
    fwrite($pipe, $message);
    pclose($pipe);
}
exit(0);
