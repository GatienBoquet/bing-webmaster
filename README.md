# Bing Webmaster Codex Skill

Use Microsoft Bing Webmaster Tools from Codex to audit Bing SEO visibility, crawl issues, URL index status, search traffic, sitemap feeds, and URL submissions.

This repository packages a reusable Codex skill plus a small Python helper for the official Bing Webmaster API. It is designed for SEO operators, site owners, and AI coding agents that need repeatable Bing Webmaster evidence instead of manual portal screenshots.

## What This Skill Does

- Lists verified Bing Webmaster Tools properties for an authenticated account.
- Checks Bing search traffic and ranking stats for a verified site.
- Reviews Bing crawl issues for URLs that need technical SEO attention.
- Looks up URL index information and traffic for individual pages.
- Lists inbound links and pages with inbound links.
- Checks URL submission quota before submitting pages.
- Submits URLs, URL batches (up to 500), or sitemap feeds, guarded by `--dry-run` / `--allow-write`.
- Documents API key and OAuth usage for Microsoft Bing Webmaster API workflows.

## Best For

- Bing SEO audits
- Technical SEO monitoring
- Crawl issue triage
- URL indexing checks
- Sitemap and feed submission workflows
- Comparing Bing Webmaster Tools data with Google Search Console
- Agent-ready website diagnostics in Codex

## Repository Contents

~~~text
.
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   `-- api-reference.md
|-- scripts/
|   `-- bing_webmaster.py
`-- tests/
    `-- test_bing_webmaster.py
~~~

## Install The Skill

Clone or copy this folder into your Codex skills directory:

~~~powershell
git clone https://github.com/GatienBoquet/bing-webmaster.git "$env:USERPROFILE\.codex\skills\bing-webmaster"
~~~

On macOS or Linux:

~~~bash
git clone https://github.com/GatienBoquet/bing-webmaster.git ~/.codex/skills/bing-webmaster
~~~

Then invoke it in Codex:

~~~text
Use $bing-webmaster to audit Bing crawl issues and traffic for https://example.com/
~~~

## Connect Bing Webmaster Tools

The simplest authentication method is an API key.

1. Open [Bing Webmaster Tools](https://www.bing.com/webmasters/).
2. Sign in.
3. Add and verify your site.
4. Open **Settings > API Access**.
5. Generate an API key.
6. Set it only in your local shell session:

~~~powershell
$env:BING_WEBMASTER_API_KEY = "your-api-key"
~~~

~~~bash
export BING_WEBMASTER_API_KEY="your-api-key"
~~~

Do not commit API keys, OAuth access tokens, refresh tokens, .env files, or credential exports.

## Quick API Checks

List verified sites:

~~~powershell
python scripts/bing_webmaster.py sites
~~~

Check Bing traffic stats:

~~~powershell
python scripts/bing_webmaster.py traffic --site-url "https://example.com/"
~~~

Check Bing crawl issues:

~~~powershell
python scripts/bing_webmaster.py crawl-issues --site-url "https://example.com/"
~~~

Check URL submission quota:

~~~powershell
python scripts/bing_webmaster.py quota --site-url "https://example.com/"
~~~

Preview a URL submission without sending it:

~~~powershell
python scripts/bing_webmaster.py submit-url --site-url "https://example.com/" --url "https://example.com/page" --dry-run
~~~

Submit only after confirming the target URL and quota. Write commands refuse to run without `--dry-run` or `--allow-write`:

~~~powershell
python scripts/bing_webmaster.py submit-url --site-url "https://example.com/" --url "https://example.com/page" --allow-write
~~~

Submit a batch of up to 500 URLs from a file (one URL per line):

~~~powershell
python scripts/bing_webmaster.py submit-batch --site-url "https://example.com/" --url-file urls.txt --dry-run
~~~

Check inbound links for a page:

~~~powershell
python scripts/bing_webmaster.py links --site-url "https://example.com/" --url "https://example.com/page"
~~~

Run `python scripts/bing_webmaster.py --help` for every command.

## Safety Model

Read-only calls are preferred by default. Write actions such as URL submission, feed submission, site verification, blocked URL changes, and site moves should be run only after the exact target is confirmed.

Every write command (`submit-url`, `submit-batch`, `submit-feed`, and `raw` calls to write methods or with POST) refuses to run unless it gets `--dry-run` or `--allow-write`. `--dry-run` prints the HTTP method, URL with the API key masked, auth mode, and body without calling Bing.

## Environment Variables

~~~text
BING_WEBMASTER_API_KEY       API key from Bing Webmaster Tools
BING_WEBMASTER_ACCESS_TOKEN  OAuth bearer token for Bing Webmaster API
~~~

API key auth is usually enough for personal and site-owner workflows. OAuth is useful for delegated applications that need the webmaster.read or webmaster.manage scopes. When a token is set, the helper sends it as a Bearer header to www.bing.com and does not send the API key.

## Tests

The tests run offline and need only the Python standard library:

~~~bash
python3 -m unittest discover -s tests
~~~

## Microsoft Bing Webmaster API References

- [Bing Webmaster API documentation](https://learn.microsoft.com/en-us/bingwebmaster/)
- [Getting access to the Bing Webmaster Tools API](https://learn.microsoft.com/en-us/bingwebmaster/getting-access)
- [Bing Webmaster OAuth 2.0](https://learn.microsoft.com/en-us/bingwebmaster/oauth2)
- [IWebmasterApi method reference](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi?view=bing-webmaster-dotnet)

## Keywords

Bing Webmaster API, Bing Webmaster Tools, Codex skill, SEO audit, technical SEO, crawl issues, URL indexing, URL submission, sitemap submission, search traffic, webmaster tools automation, Microsoft Bing SEO.
