# System design for frontend tasks

A browser tab is a node in the distributed system: it has a cache, a
connection budget, a failure story and a deploy cycle you do not control (the
user may keep the tab open for days). Every step of the pass applies; the
components just have different names.

## Scope and NFRs, client version

| NFR | Frontend question |
| --- | --- |
| Scale | How many items in the list for the biggest tenant? How many concurrent tabs per user? How many tabs hit the API at 9:00? |
| Latency | What does the user see while waiting: skeleton, stale data, spinner, nothing? Is the action optimistic? |
| Availability | What happens when the API is slow, a remote module fails to load, the socket drops, the token expires mid-session? |
| Consistency | After a mutation, which cached queries must change? Can two tabs disagree? Can the list show an item that was just deleted? |
| Security | Tokens in memory/httpOnly cookies, not `localStorage`; no PII in URLs or analytics; sanitise anything rendered as HTML. |
| Cost | Bundle size per route; requests per screen; third-party scripts. |
| Compatibility | Old client bundles talking to a new API after a deploy; shared singleton versions across micro-frontends. |

## Estimate, client version

- Items per list × bytes per item → payload per page; past ~1 MB per request
  or a few hundred rows rendered at once, paginate and virtualise.
- Requests per screen × round-trip latency (50-150 ms on mobile) → time to
  interactive; sequential waterfalls multiply it.
- Initial JS per route; each remote module adds its own chunk and its own
  failure mode.
- Events per second on a socket × subscribers per tab → render budget; batch
  socket events into one state update per animation frame when they are
  frequent.

## As-is, client version

Map the real data-fetching layer before proposing one:

- Server-state cache (TanStack Query / SWR / RTK Query / Apollo): query keys,
  `staleTime`, invalidation points, where mutations live.
- Client state (Zustand/Redux/context) vs URL state (filters, pagination,
  selected id) vs server state. Each has an owner; duplicates are bugs.
- Existing shared components for lists, pagination, infinite scroll,
  virtualisation, forms, uploads.
- Real-time transport already in place (socket hub, SSE, polling hooks) and
  its reconnect story.
- Micro-frontend boundaries: what the host exposes, which deps are
  singletons, how a remote failure is isolated, how routes are mounted.
- Error and loading conventions: error boundaries, retry UI, toasts.

## To-be, client version

**Data fetching.** One query per screen-level concern, keyed by every
parameter that changes the result. `staleTime` by data class: reference data
(dictionaries, settings) minutes; lists seconds; live data push-invalidated.
Prefetch on hover/route-match for the next screen when latency is visible.

**Mutations.** Invalidate by key after success; optimistic update only when
the rollback UI is designed and the server rejects rarely. Send an idempotency
key for non-idempotent actions the user can double-click. Disable the button
while in flight; it is the cheapest dedup.

**Lists.** Cursor pagination over offset for anything that grows; infinite
scroll with windowing past a few hundred rows; server-side filters and sort
for large sets; debounce search input (200-400 ms) and cancel stale requests.

**Real-time.** Choose polling / SSE / WebSocket by freshness and direction
(see `patterns.md` §5). Design reconnect with a resume cursor so no event is
lost; show a "reconnecting" state; fall back to polling when the socket is
blocked by a proxy. Push events should update the cache (patch the query) or
trigger a refetch, not bypass it.

**Failure isolation.** Each remote module, widget or third-party script gets
an error boundary and a fallback. A timeout on data fetching renders the rest
of the page. Token expiry is handled once, centrally (refresh or redirect),
not per request.

**Bundle and delivery.** Route-level code splitting; keep shared singletons
(React, router, UI kit) single and version-aligned across host and remotes;
hashed asset filenames with immutable caching; a CDN in front of static
output; measure the bundle in CI with a budget.

**Micro-frontend specifics.** A remote is a deployable unit with its own
release cycle: contracts between host and remote (exposed modules, props,
events) are public APIs and must be backward compatible for at least one
release; shared dependency versions are a coordination problem treated like a
DB migration (expand → migrate → contract); a failing remote must degrade to a
placeholder, not break the host route.

**Forms and uploads.** Validate on the client for UX and on the server for
truth; upload large files directly to object storage with pre-signed URLs and
show progress; chunk and resume for very large files.

**Observability.** Web vitals per route, JS errors tagged with release and
remote version, API latency from the client's view, socket reconnect counts,
remote-load failures. These are the SLIs for a frontend feature.

## Deep-dive questions that bite on the client

1. Double submit / retry of a non-idempotent action.
2. Stale list after a mutation in another tab or by another user.
3. Growing list with offset pagination (duplicates and skips).
4. Hot tenant with 50k rows in a "load everything" dropdown.
5. Socket drops for 30 s; which events were missed and how are they replayed?
6. Remote module 404 after a deploy because the host cached an old manifest.
7. Token expires during a long form; is the draft lost?
8. Request waterfall: 6 sequential calls before first paint.
9. Third-party script down blocks page load (load async, with timeout).
10. Timezone and locale drift between client and server for dates and
    currency.

## Typical frontend design check (L1)

```
Touches: EmployeeList (TanStack Query key ['employees', filters]) + /api/employees.
Load: biggest tenant ~12k employees; current page size 50; server-side filter exists.
Risk: new "department" filter is not part of the query key → stale list on change. Add it to the key; keep filter in URL state so links are shareable.
Nothing else changes; no new transport, no new cache.
```
