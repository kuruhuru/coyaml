# Configuration & Templates

<!-- 
Explain how `resolve_templates()` works:
- env: `${{ env:VAR[:DEFAULT] }}`
- file: `${{ file:PATH }}`
- yaml: `${{ yaml:PATH }}`
- config: `${{ config:dot.notation.path }}`
Discuss recursion, error handling, defaults.
-->

```yaml
database:
  user: ${{ env:DB_USER:default_user }}
  init_sql: ${{ file:./scripts/init.sql }}
app:
  settings: ${{ yaml:./configs/extra.yaml }}
  url: "postgresql://${{ config:database.user }}@localhost/db"
```