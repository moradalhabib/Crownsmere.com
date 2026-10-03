# Crownsmere inbox filter

Every email sent to **hello@crownsmere.com** is read by Claude, which decides whether it deserves Alaa's attention:

- **Genuine** (client enquiries, website form leads, solicitors, brokers, official business mail): forwarded to **Alaa.Q@crownsmere.com** with a one-line summary on top and the original attached. Pressing Reply answers the original sender.
- **Junk** (spam, phishing, cold sales pitches, newsletters, unrelated mail): logged and not forwarded.

Nothing is ever deleted. The hello@ mailbox keeps a copy of everything, so a wrongly filtered email can always be found there.

**Safety:** when in doubt, the filter forwards. If Claude is unreachable, declines to answer, or is less than 75% sure an email is junk, the email goes to Alaa anyway, marked "Unfiltered" or with its confidence score.

## Files

| File | What it is |
|---|---|
| `filter.php` | The filter. cPanel pipes each incoming email into it. |
| `config.sample.php` | Settings template. Copy it to `config.php` and add your API key. |
| `composer.json` | Installs the official Anthropic PHP SDK. |
| `tests/*.eml` | Sample emails for a dry run. |

## One-time setup in cPanel

You need: Namecheap cPanel hosting, an Anthropic API key, and about 20 minutes.

### 1. Create the two mailboxes

cPanel, **Email Accounts**, **Create**:

- `hello@crownsmere.com` (the public address on the website and in the contact form)
- `alaa.q@crownsmere.com` (Alaa's private inbox, never published)

Then open **Email Deliverability** and click **Repair** on any record that shows a problem, so the SPF and DKIM records are valid. Mail forwarded by the filter is far less likely to land in spam.

> **DNS note:** the website is hosted on GitHub Pages, but email is hosted on cPanel. The domain's **MX** record must still point at your Namecheap hosting server. If you edited the DNS for GitHub Pages, change only the `@` A records and the `www` CNAME, and leave the MX, `mail` and TXT (SPF/DKIM) records alone. **Email Deliverability** shows whether they are correct.

### 2. Get an Anthropic API key

Sign in at [platform.claude.com](https://platform.claude.com), add billing, then go to **Settings, API keys, Create key**. Copy the key (it starts with `sk-ant-`).

Each email costs roughly one US cent to classify.

### 3. Upload the filter (outside public_html)

In **File Manager**, create a folder in your home directory, **not** inside `public_html`:

```
/home/YOUR-CPANEL-USERNAME/crownsmere-filter/
```

Upload `filter.php`, `composer.json`, `config.sample.php` and the `tests` folder into it.

### 4. Install and configure (cPanel Terminal)

Open **Terminal** in cPanel and run:

```bash
cd ~/crownsmere-filter
php -v                      # must be 8.1 or newer (set it in "Select PHP Version" / "MultiPHP Manager")
composer install --no-dev   # if "composer: command not found", see Troubleshooting
cp config.sample.php config.php
chmod 755 filter.php
chmod 600 config.php
```

Edit `config.php` (File Manager, **Edit**) and paste your API key into `anthropic_api_key`. The other settings are already filled in for Crownsmere.

### 5. Dry run (sends nothing)

```bash
php filter.php --dry-run < tests/client-enquiry.eml
php filter.php --dry-run < tests/seo-pitch.eml
```

You should see `FORWARD [client_enquiry] ...` for the first and `DISCARD [sales_pitch] ...` for the second. An "Unfiltered" result means the API key or network is not working yet. Check `filter.log`.

### 6. Switch it on

cPanel, **Forwarders**, **Add Forwarder**:

- **Address to forward:** `hello`, domain `crownsmere.com`
- Click **Advanced Options**, then choose **Pipe to a Program**
- **Path:** `crownsmere-filter/filter.php`

Save. cPanel now delivers each email to the hello@ mailbox *and* to the filter.

### 7. Test for real

From a personal email account, send two emails to hello@crownsmere.com: one that reads like a client enquiry, and one that reads like a sales pitch. Within a minute or so, only the first should arrive at Alaa.Q@crownsmere.com, with the filter's summary on top. Both are recorded in `filter.log`.

## Everyday use

- **`filter.log`** has one line per email: time, sender, subject, decision and reason. Message bodies are never logged.
- **Always forward a sender:** add their address or domain (e.g. `rightmove.co.uk`) to `always_forward` in `config.php`.
- **Never forward a sender:** add them to `never_forward`.
- **Stricter or looser:** `min_confidence_to_discard` (default `0.75`). Raise it to forward more borderline mail; lower it to filter more aggressively.
- **Something important was filtered?** It is still in the hello@ mailbox (Webmail). Add the sender to `always_forward`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `composer: command not found` | Run `curl -sS https://getcomposer.org/installer \| php` then `php composer.phar install --no-dev`. |
| Senders get a bounce mentioning "pipe" | The first line of `filter.php` must point at PHP. Run `which php`; if it is not `/usr/local/bin/php`, change line 1 to match. Also make sure the file is `chmod 755` and was uploaded with Unix (LF) line endings. |
| Everything arrives marked "Unfiltered" | Claude could not be reached. Check the API key and billing, then look at `filter.log` for the error type. |
| Nothing arrives at Alaa at all | Check `filter-error.log` in the same folder, then confirm `sendmail_path` in `config.php` (`which sendmail`). |
| Forwarded mail lands in spam | Run **Email Deliverability**, **Repair** in cPanel for SPF and DKIM. |
