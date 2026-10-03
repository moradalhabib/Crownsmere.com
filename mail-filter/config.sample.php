<?php
/**
 * Copy this file to config.php (same folder) and fill in your API key.
 * config.php is git-ignored: never commit it or upload it anywhere public.
 */
return [
    // Create a key at https://platform.claude.com (Settings > API keys).
    'anthropic_api_key' => 'sk-ant-REPLACE-ME',

    // The Claude model that reads each email.
    'model' => 'claude-opus-5-5',

    // Where genuine mail goes, and who it appears to come from.
    'forward_to' => 'Alaa.Q@crownsmere.com',
    'forward_from' => 'hello@crownsmere.com',
    'forward_from_name' => 'Crownsmere Inbox',

    // Mail Claude marks "discard" is still forwarded if its confidence is below this.
    'min_confidence_to_discard' => 0.75,

    // Addresses or whole domains that skip the AI. Lower case.
    'always_forward' => [
        // 'solicitor@example-law.co.uk',
        // 'rightmove.co.uk',
    ],
    'never_forward' => [
        // 'spammy-seo-agency.com',
    ],

    // Email Alaa a short daily list of what was held back (needs the cron job in README).
    'daily_digest' => true,

    // Usually correct on cPanel. Run `which sendmail` in the cPanel Terminal if unsure.
    'sendmail_path' => '/usr/sbin/sendmail',

    // One JSON line per email: who, subject, decision, reason. Bodies are never logged.
    'log_file' => __DIR__ . '/filter.log',
];
