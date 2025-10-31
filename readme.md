# Excalimap

Escalimap is the tool used by OCD to generate the Active Directory mindmap from markdown.

Why i forked the project ?

Because i wanted to collaborate on mindmap and i think this is the best way to do it with self hosted solution. However, escalimap is focus on AD mindmap requirements and for my mindmap I had to edit it.
 

# How to use the project

If you are lazy start excalidraw like this :

```bash
docker run --rm -dit --name excalidraw -p 5000:80 excalidraw/excalidraw:latest
```

Then to generate your mindmap select your project directory:

```bash
python3 main.py -f <source_file> -o <excalidraw_file_destination>
for example with the ocd-mindmap project
python3 main.py -f ../ocd-mindmaps/excalimap/mindmap/ad/ -o output/ad.excalidraw
```

There is also a development mode :) 

You should install some prerequisites first:
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Then you can execute :
```bash
./scripts/watch.py -f ../ocd-mindmaps/excalimap/mindmap/ad/
```

When you will edit file in ../ocd-mindmaps/excalimap/mindmap/ad/
it will generate a new version in output/minmap.excalidraw.

Then, you can directly open it with excalidraw vs code extension or load it in your browser.


## Syntax Table of Contents

1. [Basic Structure](#basic-structure)
2. [Containers](#containers)
3. [Titles](#titles)
4. [Items](#items)
5. [Output Boxes](#output-boxes)
6. [Links](#links)
7. [CVE Marking](#cve-marking)
8. [Nesting](#nesting)
9. [Configuration File](#configuration-file)
10. [Complete Examples](#complete-examples)

---

## Basic Structure

Each markdown file represents one container (section) in the mindmap. A typical file structure:

```markdown
# Container Name
Description...

## Title 1
- Item 1
  - Item 2

## Title 2
- Item 1
```

**Hierarchy:**
- `#` = Container (top-level section)
- `##` = Title (subsection header)
- `-` = Item (content: info or command)
- Indentation (2 spaces) = Nesting

---

## Containers

**Syntax:** `# Container Name`

Containers are the top-level sections of your mindmap. Each markdown file should have exactly one container.

```markdown
# No Credentials
```

**Styling:**
- Background color can be customized in `conf.yml` under `container_color:`
- Container name will be displayed as a header
- All content is wrapped inside this container box

---

## Titles

**Syntax:** `## Title Name`

Titles are subsection headers within a container.

### Basic Title

```markdown
## Scan network
```

### Title with Output Box

Connect a title to an output box using `>>>`:

```markdown
## Scan network >>> Vulnerable host
```

This creates an arrow from "Scan network" to an output box labeled "Vulnerable host".

### Multiple Output Boxes

Chain multiple outputs:

```markdown
## Dcsync >>> Domain Admin || Lateral move || Crack hash
```

- `>>>` chains outputs sequentially
- `||` creates parallel outputs (branches)

Result: Dcsync → Domain Admin
                 → Lateral move
                 → Crack hash

---

## Items

Items are the content inside titles. Two types: **Info** (plain text) and **Command** (code blocks).

### Info Items

**Syntax:** `- Plain text`

```markdown
- Administrators, Domain Admins, or Enterprise Admins
- This is informational text
```

**Renders as:** Regular text boxes

### Command Items

**Syntax:** `` - `command text` ``

Commands are wrapped in backticks:

```markdown
- `nmap -sP -p <ip>`
- `mimikatz lsadump::dcsync /domain:<target_domain>`
```

**Renders as:** Code-styled boxes with monospace font

**Tool Detection:**
The first word of a command is automatically matched against the `tools:` section in `conf.yml`. If found, an icon is added:

```markdown
- `nmap -sP <ip>`
```

If `nmap` is defined in `conf.yml` with an icon, the icon will appear next to the command.


### Multiline command items

**Syntax:** 

\```

Your multiline command

Or text

Or whatever.
\```

**Renders as:** A multilines item.

## Output Boxes

Output boxes create visual connections between sections. They represent results, transitions, or next steps.

### Item-Level Outputs

Add outputs to individual items:

```markdown
- `nmap -sP <ip>` >>> Vulnerable host
```

### Chained Outputs

Create a sequence of output boxes:

```markdown
## Out box >>> out A >>> out B
```

Result: Out box → out A → out B

### Parallel Outputs (Branching)

Use `||` to create branches:

```markdown
## Out box >>> out A || out B
```

Result: Out box → out A
                → out B

### Complex Output Chains

Combine both:

```markdown
## Out box >>> out A >>> out B || out C >>> out D
```

Result: Out box → out A → out B
                        → out C → out D

### Nested Item Outputs

```markdown
- `1 Command` >>> out box of command 2 & 2bis
  - `2 Command`
    - `3 Command` >>> out box of command 3
  - `2bis command`
```

Creates arrows from commands to their respective output boxes.

**Output Colors:**
Define output box colors in `conf.yml` under `out:` section:

```yaml
out:
  "Vulnerable host": color_name
  "Domain Admin": admin_color
```

---

## Links

Attach URLs to items by placing the link on the next line:

```markdown
- `command with link`
  - `sub command with link`
[https://example.com](https://example.com)
```

The URL is associated with the previous item (not displayed as separate text).

**For tools:** Define links in `conf.yml`:

```yaml
tools:
  nmap:
    icon: nmap
    link: https://github.com/nmap/nmap
```

---

## CVE Marking

Mark items as CVE-related to apply special styling.

### Method 1: Inline Marker

```markdown
- `command CVE` @CVE@
- Bloc CVE @CVE@
```

### Method 2: HTML Comment

```markdown
<!-- cve -->
```

Place this comment above a title or item to mark it as CVE-related.

**Example:**

```markdown
## DNS Admin
- DNSadmins abuse (CVE-2021-40469) @CVE@ >>> Admin
```

**Styling:** CVE items get a distinct background color (defined in `config.py` as `cve_color`).

---

## Nesting

Indentation creates parent-child relationships. Use **2 spaces** per level.

### Basic Nesting

```markdown
- Level 1
  - Level 2
    - Level 3
```

### Nested Commands

```markdown
- `parent command`
  - `child command 1`
  - `child command 2`
    - `grandchild command`
```

### Mixed Nesting

```markdown
- Info text
  - `command under info`
    - More info under command
```

**Rules:**
- Always use 2 spaces for indentation
- Items can nest up to multiple levels
- Both info and command items can be nested under each other

---

## Configuration File

Each mindmap folder needs a `conf.yml` file alongside the markdown files.

### Minimal Configuration

```yaml
main_title: "Your Mindmap Title"
main_title_logo: ocd  # or custom logo name

matrix:
  - ['file1', 'file2']  # Layout grid (no .md extension)

tools: {}
color_id: {}
container_color: {}
out: {}
```

### Full Configuration Example

```yaml
main_title: Active Directory Mindmap
main_title_logo: ocd

# Layout grid: 2D array defining positions
# Empty strings ('') create blank cells
matrix:
  - ['no_creds'   , 'valid_user', 'authenticated']
  - ['low_hanging', 'mitm'      , ''            ]
  - ['authors'    , 'crack_hash', ''            ]

# Tool definitions for auto-icon/link
tools:
  nmap:
    icon: nmap
    link: https://github.com/nmap/nmap
  nxc:
    icon: nxc
    link: https://github.com/Pennyw0rth/NetExec
  bloodhound-python:
    icon: bloodhound
    link: https://github.com/dirkjanm/BloodHound.py
  mimikatz:
    icon: mimikatz
    link: https://github.com/gentilkiwi/mimikatz

# Named color palette (hex colors)
color_id:
  no_creds: "#D0CEE2"
  valid_user: "#B4C7E7"
  hash: "#FFE699"
  access: "#C5E0B4"

# Assign colors to containers (by container name)
container_color:
  "No Credentials": no_creds
  "Valid Credentials": valid_user

# Assign colors to output boxes (by output text)
out:
  "Username": no_creds
  "Hash found": hash
  "Domain Admin": access
  "Vulnerable host": hash
```

### Matrix Layout

The `matrix` defines the spatial layout:

```yaml
matrix:
  - ['file1', 'file2', 'file3']  # Row 1
  - ['file4', ''     , 'file5']  # Row 2 (middle cell empty)
```

- Each row is a Python list
- Columns are created by transposing (`zip(*matrix)`)
- Empty cells: use `''` (empty string)
- File names: exclude `.md` extension

**Visual result:**

```
┌────────┐  ┌────────┐  ┌────────┐
│ file1  │  │ file2  │  │ file3  │
└────────┘  └────────┘  └────────┘

┌────────┐              ┌────────┐
│ file4  │              │ file5  │
└────────┘              └────────┘
```

---

## Complete Examples

### Example 1: Simple Scan Section

**File:** `scan.md`

```markdown
# Network Scanning

## Discover hosts >>> Live hosts
- `nmap -sn 10.0.0.0/24`
- `nmap -sP -p 10.0.0.0/24`

## Port scanning >>> Open ports
- Full TCP scan
  - `nmap -p- -sV 10.0.0.1`
- Quick scan
  - `nmap --top-ports 100 10.0.0.1`
```

**File:** `conf.yml`

```yaml
main_title: Network Pentesting
main_title_logo: ocd

matrix:
  - ['scan']

tools:
  nmap:
    icon: nmap
    link: https://nmap.org

color_id:
  scan_color: "#D0CEE2"
  result_color: "#FFE699"

container_color:
  "Network Scanning": scan_color

out:
  "Live hosts": result_color
  "Open ports": result_color
```

### Example 2: Complex Attack Path

**File:** `privesc.md`

```markdown
# Privilege Escalation

## Kerberoasting >>> Hash TGS
- Find SPNs
  - `GetUserSPNs.py -request -dc-ip <dc_ip> <domain>/<user>`
  - `Rubeus.exe kerberoast`

## ACL Abuse >>> Domain Admin || Lateral move
- GenericAll on User
  - Change password
    - `net user <user> <password> /domain` >>> User with clear text pass
  - Add SPN
    - `targetedKerberoast.py -d <domain> -u <user>` >>> Hash found (TGS)
- GenericAll on Computer
  - RBCD attack
    - `rbcd.py -d <domain> -u <user>` >>> Access

## Known Exploits @CVE@
- PrintNightmare (CVE-2021-1675) @CVE@ >>> SYSTEM shell
  - `CVE-2021-1675.py <domain>/<user>:<pass>@<target>`
[https://github.com/cube0x0/CVE-2021-1675](https://github.com/cube0x0/CVE-2021-1675)
```

**File:** `conf.yml`

```yaml
main_title: AD Privilege Escalation
main_title_logo: ocd

matrix:
  - ['privesc']

tools:
  GetUserSPNs.py:
    icon: impacket
    link: https://github.com/fortra/impacket
  Rubeus.exe:
    icon: rubeus
    link: https://github.com/GhostPack/Rubeus
  net:
    link: https://learn.microsoft.com/en-us/windows-server/

color_id:
  privesc: "#E7C6B4"
  creds: "#FFE699"
  access: "#C5E0B4"

container_color:
  "Privilege Escalation": privesc

out:
  "Hash TGS": creds
  "Domain Admin": access
  "Lateral move": access
  "User with clear text pass": creds
  "Hash found (TGS)": creds
  "Access": access
  "SYSTEM shell": access
```

### Example 3: Multi-Column Layout

**Files:** `recon.md`, `exploit.md`, `post.md`

**recon.md:**
```markdown
# Reconnaissance

## Port Scan >>> Open services
- `nmap -sV <target>`

## Service Enum >>> Vulnerabilities
- `nmap --script vuln <target>`
```

**exploit.md:**
```markdown
# Exploitation

## Web App >>> Shell
- SQL injection
  - `sqlmap -u <url>`
- RCE exploit
  - `exploit.py <target>` >>> Initial access
```

**post.md:**
```markdown
# Post-Exploitation

## Enumerate >>> Credentials
- `mimikatz sekurlsa::logonpasswords`

## Pivot >>> Internal network
- `proxychains nmap <internal_ip>`
```

**conf.yml:**
```yaml
main_title: Full Pentest Workflow
main_title_logo: ocd

matrix:
  - ['recon', 'exploit', 'post']

tools:
  nmap:
    icon: nmap
    link: https://nmap.org
  sqlmap:
    icon: sqlmap
    link: https://sqlmap.org
  mimikatz:
    icon: mimikatz
    link: https://github.com/gentilkiwi/mimikatz

color_id:
  recon: "#D0CEE2"
  exploit: "#FFB3B3"
  post: "#C5E0B4"

container_color:
  "Reconnaissance": recon
  "Exploitation": exploit
  "Post-Exploitation": post

out:
  "Open services": recon
  "Vulnerabilities": exploit
  "Shell": exploit
  "Initial access": exploit
  "Credentials": post
  "Internal network": post
```

---

## Best Practices

1. **One container per file** - Each `.md` file = one container
2. **Consistent naming** - Match output box names across files for visual consistency
3. **Tool definitions** - Add all tools to `conf.yml` for automatic icon detection
4. **Color scheme** - Use consistent color palette in `color_id` and reference it
5. **Indentation** - Always use 2 spaces, never tabs
6. **Output logic** - Use outputs to show progression/results (e.g., "Scan → Vulns → Exploit → Access")
7. **CVE marking** - Mark exploits with `@CVE@` for visual distinction
8. **Comments in commands** - Keep placeholder syntax like `<target>`, `<domain>`, `<ip>` for clarity

---

## Common Patterns

### Pattern: Attack Progression

```markdown
## Initial Access >>> Foothold
- Exploit vulnerability
  - `exploit.py <target>` >>> Shell

## Enumeration >>> Credentials
- Extract credentials
  - `mimikatz` >>> Hash found

## Lateral Movement >>> Domain Admin
- Pass-the-Hash
  - `psexec.py -hashes <hash> <target>` >>> SYSTEM
```

### Pattern: Multiple Techniques

```markdown
## Privilege Escalation
- Technique 1 >>> Access
  - `command1`
- Technique 2 >>> Access
  - `command2`
- Technique 3 >>> Access
  - `command3`
```

All techniques lead to the same output ("Access").

### Pattern: Conditional Paths

```markdown
## Authentication >>> Valid creds || Failed
- Try password spray
  - `kerbrute passwordspray`
```

Shows two possible outcomes: success or failure.

---

## Troubleshooting

**Issue:** Tool icon not showing
- **Fix:** Ensure tool name (first word of command) matches key in `conf.yml` `tools:` section
- **Example:** `` `nmap -sV` `` requires `nmap:` in tools section

**Issue:** Output box wrong color
- **Fix:** Check `out:` section in `conf.yml` - output text must match exactly (case-sensitive)

**Issue:** Incorrect nesting
- **Fix:** Use exactly 2 spaces per indentation level, no tabs

**Issue:** Container not colored
- **Fix:** Container name in `# Container Name` must match key in `container_color:` section

**Issue:** File not appearing in output
- **Fix:** Verify filename (without `.md`) is in `matrix:` array in `conf.yml`

---

## Advanced: Special Characters

- **Ampersand in output:** `>>> out A & out B` - Use `&` in output text
- **Multiple words:** `>>> User with clear text pass` - Spaces allowed
- **Quotes in commands:** `` `command "quoted text"` `` - Works in backticks
- **Pipes in commands:** `` `command | grep output` `` - Pipe character OK

---

## Real-World Examples from AD Mindmap

The Active Directory mindmap (`excalimap/mindmap/ad/`) contains extensive real-world examples. Here are key patterns used:

### Complex Multi-Level Nesting (from adcs.md)

```markdown
## ESC7
- Manage CA
  - `certipy ca -ca <ca_name> -add-officer '<user>'` >>> ESC7 Manage certificate
- Manage certificate
  - `certipy ca -ca <ca_name> -enable-template '<template>'`
    - `certipy req -username <user>@<domain> -template '<template>'`
      - error, but save private key and get issue request
  - Issue request
    - `certipy ca -u <user> -ca <ca_name> -issue-request <request_id>`
      - `certipy req -u <user> -ca <ca_name> -retreive <request_id>` >>> Pass the certificate
```

**Pattern:** Multi-step attack chain with nested commands showing the exact sequence.

### Complex Output Chains (from adcs.md)

```markdown
## Enumeration >>> Web enrollement || Vulnerable template || Vulnerable CA || Misconfigured ACL || Vulnerable PKI Object AC
```

**Pattern:** Single enumeration phase leads to multiple possible attack paths (5 parallel branches).

### Descriptive Intermediates (from sccm.md)

```markdown
## Elevate-3:Automatic client push Simple user >>> Relay ntlm
- Create DNS A record for non existing computer x
  - `dnstool.py -u '<domain>\<user>' -r <newcomputer>.<domain> -a add -t A -d <attacker_ip> <dc_ip>`
    - Enroll new computer x in AD then remove host SPN from the machine account
      - `setspn -D host/<newcomputer> <newcomputer>`
        - wait 5m for client push
          - `ntlmrelayx.py -tf <no_signing_target> -smb2support -socks`
            - cleanup
```

**Pattern:** Mix of commands and descriptive text showing workflow steps. Notice "wait 5m" and "cleanup" as info items.

### Conditional Logic (from mitm.md)

```markdown
## Listen >>> Hash NTLMv1 or NTLMv2 || Username || Credentials (ldap/http)
- `responder -l <interface> #use --lm to force downgrade`

## NTLM relay
- SMB -> LDAP(S)
  - NTLMv1
    - remove mic (no CVE needed) >>> see LDAP(S)
  - NTLMv2
    - Remove mic (CVE-2019-1040) @CVE@ >>> see LDAP(S)
```

**Pattern:** Shows different techniques based on protocol version. Uses output references like "see LDAP(S)" to point to another section.

### Procedural Sequences (from delegation.md)

```markdown
## Constrained delegation
- With protocol transition (any) UAC: TRUST_TO_AUTH_FOR_DELEGATION
  - Get TGT for user
    - Request S4u2self
      - Request S4u2proxy
  - `Rubeus.exe hash /password:<password>`
    - `Rubeus.exe asktgt /user:<user> /domain:<domain> /aes256:<AES>`
      - `Rubeus.exe s4u /ticket:<ticket> /impersonateuser:<admin> /msdsspn:<spn> /ptt`
        - Altservice HTTP/HOST/CIFS/LDAP >>> Kerberos TGS
```

**Pattern:** Nested indentation shows exact command sequence where each step depends on the previous.

### Multiple Techniques to Same Goal (from lat_move.md)

```markdown
## Clear text Password >>> Admin
- Interactive-shell - psexec >>> Authority/System
  - `psexec.py <domain>/<user>:<password>@<ip>`
  - `psexec.exe -AcceptEULA \\<ip>`
  - `psexecsvc.py <domain>/<user>:<password>@<ip>`
- Pseudo-shell (file write and read)
  - `atexec.py <domain>/<user>:<password>@<ip> "command"`
  - `smbexec.py <domain>/<user>:<password>@<ip>`
  - `wmiexec.py <domain>/<user>:<password>@<ip>`
```

**Pattern:** Multiple tools/commands at same indentation level = alternative methods to achieve same goal.

### Cross-References (from mitm.md)

```markdown
- To HTTP
  - Relay to CA web enrollement >>> ESC8
  - Relay to WSUS >>> WSUS
```

**Pattern:** Output boxes referencing other sections/techniques by name. This creates visual connections between related attacks.

### BloodHound Queries (from delegation.md)

```markdown
## Find delegation
- With BloodHound
  - Unconstrained
    - `MATCH (c:Computer {unconstraineddelegation:true}) RETURN c`
    - `MATCH (c:User {unconstraineddelegation:true}) RETURN c`
  - Constrained
    - `MATCH p=((c:Base)-[:AllowedToDelegate]->(t:Computer)) RETURN p`
```

**Pattern:** Cypher queries are treated as commands (backticks) alongside regular shell commands.

### State Transitions (from sccm.md)

```markdown
## Creds-1 No credentials >>> NAA credentials || User + Pass
## Elevate-1:Relay on site systems Simple user >>> Admin on Site system
## Elevate-2:Force client push Simple user >>> Admin
```

**Pattern:** Title prefix shows privilege level before (`Simple user`) and output shows privilege gained (`Admin`).

### Combined Credential Types (from lat_move.md)

```markdown
## Clear text Password >>> Admin
## NT Hash
## Kerberos
## Certificate (pfx)
```

**Pattern:** Each title represents a different credential type, with techniques specific to that type.

### Inline Comments in Commands (from no_creds.md)

```markdown
- `responder -l <interface> #use --lm to force downgrade`
- `nxc smb <dc_ip> --rid-brute 10000 # bruteforcing RID`
```

**Pattern:** Comments after commands (with `#`) provide additional context without breaking command formatting.

### Numbered Technique Variants (from sccm.md)

```markdown
## Creds-1 No credentials >>> NAA credentials || User + Pass
## Elevate-1:Relay on site systems Simple user >>> Admin on Site system
## Elevate-2:Force client push Simple user >>> Admin
## Elevate-3:Automatic client push Simple user >>> Relay ntlm
## CRED-6 Loot creds >>> User + Pass
```

**Pattern:** Prefix numbering organizes related techniques (e.g., all "Creds-X" are credential extraction, all "Elevate-X" are privilege escalation).

### Warning Markers (from no_creds.md)

```markdown
- ⚠️ DHCPv6 (IPv6 prefered to IPv4)
  - `mitm6 -d <domain>`
- ⚠️ ARP Poisoning
  - `bettercap`
```

**Pattern:** Emoji/symbols to highlight dangerous or impactful techniques (though generally emojis should be used sparingly).

### Cleanup Steps (from sccm.md)

```markdown
## Cleanup
- `SharpSCCM.exe get devices -sms <SMS_PROVIDER> -sc <SITECODE>`
  - `SharpSCCM.exe remove device GUID:<GUID> -sms <SMS_PROVIDER>`
```

**Pattern:** Dedicated cleanup section for post-exploitation operational security.

### Result References (from acl.md)

```markdown
## On User
- GenericAll / GenericWrite
  - Change password
    - `net user <user> <password> /domain` >>> User with clear text pass
  - add SPN (target kerberoasting)
    - `targetedKerberoast.py -d <domain> -u <user>` >>> Hash found (TGS)
```

**Pattern:** Output describes the result format (e.g., "Hash found (TGS)") to clarify what you obtain.

## Advanced Patterns Summary

1. **Deep nesting (5-6 levels)** - Shows exact attack sequences
2. **Parallel outputs with `||`** - Single action → multiple possible outcomes
3. **State annotations** - Show before/after privilege levels in titles
4. **Cross-references** - Output boxes that reference other sections by name
5. **Inline comments** - Use `#` after commands for quick notes
6. **Mixed info/commands** - Procedural steps (info) between technical commands
7. **Technique numbering** - Organize related techniques (Creds-1, Creds-2, etc.)
8. **Protocol/version splits** - Branch based on conditions (NTLMv1 vs NTLMv2)
9. **Tool alternatives** - Multiple commands at same level = different tools for same task
10. **Descriptive outputs** - Outputs describe what you get ("Hash found", "Admin access")

## Next Steps

1. **Start with example:** Copy `excalimap/mindmap/example/` as a template
2. **Study AD examples:** Review `excalimap/mindmap/ad/*.md` for complex patterns
3. **Test incrementally:** Generate after adding each section
4. **View in Excalidraw:** Open `.excalidraw` file at https://excalidraw.com
5. **Iterate:** Adjust colors, layout, and content based on visual output

**Generate command:**
```bash
cd excalimap
python3 main.py -f mindmap/your_folder -o output/your_mindmap.excalidraw
```

**View:**
Open `output/your_mindmap.excalidraw` in https://excalidraw.com


