# John Peter Discord
Does all kinds of stuff on the [CodeDay Discord server](https://discord.gg/codeday)

# Environment Variables

## API Keys/Authentication
- `CLEVERBOT_API_KEY`: API key for authenticating to the [Cleverbot API](https://www.cleverbot.com/api/) (`john` commands)
- `RAYGUN_KEY`: API key for authenticating with [Raygun](https://raygun.com)
- `GQL_ACCOUNT_SECRET`: Secret for authenticating with a GQL API
- `DB_USERNAME`, `DB_PASSWORD`, `DB_DB`, `DB_HOST`: Authentication information for PostgreSQL database
- `CONTENTFUL_SPACE_ID`, `CONTENTFUL_ACCESS_TOKEN`: Space ID and token for authenticating with [Contentful](https://www.contentful.com/)

## Role IDs
- `ROLE_NOTIFY_EVENT`: The Discord ID for a role that gets notified when workshops/talks are coming up ("@Notify: Schedule" on the CodeDay Discord)
- `ROLE_GOLD`: The Discord ID for the "@Gold Member" role on the CodeDay Discord
- `ROLE_STUDENT`: The Discord ID for the "Community Member" role on the CodeDay Discord
- `ROLES_STAFF`: A JSON-like list of Discord IDs for staff roles ("@Staff" and "@Employee" on the CodeDay Discord)
- `ROLES_TOURNAMENT`: A JSON-like list of Discord IDs for tournament administration roles ("@Tournament Leader" and "@Employee" on the CodeDay Discord)

## Channel IDs
- `CHANNEL_COMMAND`: Seemingly unused?
- `CATEGORY`: Discord ID for channel category for team channels to live
- `CHANNEL_EVENT_ANNOUNCE`: The Discord ID for a channel where scheduled events are announced
- `CHANNEL_ERRORS`: The Discord ID for a channel for errors to be sent
- `CHANNEL_RANDOM`: The Discord ID for the #random channel
- `CHANNEL_MOD_LOG`: The Discord ID for a channel for mod logging events
- `CHANNEL_GALLERY`: The Discord ID for the showcase/gallery channel
- `CHANNEL_TEAM_LOG`: The Discord ID for a channel for team logging events
- `CHANNEL_A_UPDATE`: The Discord ID for a channel for calls to `a~update`(?)

## Misc
- `IMAGE_TAG`: Commit hash for latest GitHub commit 
