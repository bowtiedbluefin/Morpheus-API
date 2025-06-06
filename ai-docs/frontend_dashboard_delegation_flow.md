# Frontend Dashboard Design for Delegation and API Key Management

This document outlines the proposed design and user flow for the account management section of the Morpheus API Gateway frontend documentation site. It integrates the Web2 login system with the Web3 wallet delegation process required for interacting with the Morpheus network.

## 1. UI Element Placement

*   **Sidebar Integration:**
    *   Add an "Account" or "Login / Manage" button/link to the left sidebar, positioned towards the bottom (below core documentation links like Home, Auth, Chat, etc.).
    *   **Conditional Labeling:**
        *   If Logged Out (no valid JWT): Button shows "Login / Register".
        *   If Logged In: Button shows "Account Dashboard" or "Account".

## 2. Dashboard Layout (Displayed in Main Content Area)

Accessed by clicking the "Account" button in the sidebar (requires user to be logged in via JWT).

*   **A. Account Information:**
    *   Display User: Show the logged-in user's email.
    *   Logout Button: A button to terminate the JWT session.

*   **B. Wallet & Delegation Status:**
    *   **Wallet Connection:**
        *   *Disconnected State:* Show a "Connect Wallet" button (e.g., "Connect MetaMask").
        *   *Connected State:* Display the connected wallet address (e.g., `0x123...abc`), possibly with a copy-to-clipboard icon. Show a "Disconnect Wallet" button.
    *   **Delegation Status:**
        *   *Wallet Connected, No Active Delegation:* Display a message explaining the need for delegation (e.g., "Authorize the Gateway to interact with the Morpheus network on your behalf to enable API key generation."). Show a "Delegate Permissions" button (disabled if the wallet is disconnected).
        *   *Active Delegation Exists:* Display "Delegation Status: Active". Optionally show the Gateway Delegate Address and expiry date. Show a "Revoke Current Delegation" button.
        *   *Wallet Disconnected:* Message indicating wallet connection is required for delegation.

*   **C. API Key Management:**
    *   **Create Key Section:**
        *   Input Field: Optional field for "Key Name" (for user reference).
        *   Button: "Generate New API Key". **Crucially, this button must be disabled if the Delegation Status is not "Active"**. A tooltip or adjacent text should explain this dependency.
        *   Display Area: After generation, display the *full* API key here *once* with a clear warning that it won't be shown again and a copy button.
    *   **Existing Keys Section:**
        *   List/Table: Display keys generated by the user.
        *   Columns: Key Name, Key Prefix (e.g., `sk-Abc...`), Created Date.
        *   Actions per Key: "Copy Prefix" button, "Delete Key" button (requires confirmation).

## 3. User Flow & Backend Interaction Details

1.  **Login/Register:**
    *   User clicks "Login / Register" (sidebar).
    *   Frontend displays login/registration forms.
    *   Frontend -> Backend: `POST /auth/login` or `POST /auth/register`.
    *   Backend -> Frontend: JWT `access_token` and `refresh_token`.
    *   Frontend: Stores tokens securely, updates sidebar button to "Account".

2.  **Access Dashboard:**
    *   User clicks "Account" (sidebar).
    *   Frontend: Renders dashboard structure. Sends subsequent requests with JWT `Authorization: Bearer <token>` header.

3.  **Connect Wallet:**
    *   User clicks "Connect Wallet".
    *   Frontend: Uses Web3 library (e.g., ethers.js, viem) to trigger browser wallet connection.
    *   Frontend: On success, stores connected address, updates UI (shows address, enables "Delegate" button).

4.  **Delegate Permissions:**
    *   User clicks "Delegate Permissions".
    *   Frontend -> Backend: `GET /config/delegate-address` (unauthenticated endpoint needed to get `settings.GATEWAY_DELEGATE_ADDRESS`).
    *   Frontend: Uses `@metamask/delegation-toolkit` library:
        *   Constructs `Delegation` object (delegate = fetched address, delegator = connected wallet address, appropriate `caveats`).
        *   Prompts user via wallet to sign EIP-712 delegation message.
    *   Frontend -> Backend: `POST /auth/delegation` with signed delegation data in the body and JWT in the header.
    *   Backend: Verifies JWT, validates delegate address, stores signed delegation, returns success/delegation details.
    *   Frontend: Updates UI ("Delegation Status: Active", enables "Generate API Key" button).

5.  **Generate API Key:**
    *   User provides optional name, clicks "Generate New API Key".
    *   Frontend -> Backend: `POST /auth/keys` with optional name and JWT.
    *   Backend -> Frontend: Newly generated full API key.
    *   Frontend: Displays full key *once* with copy button. Fetches updated key list.

6.  **List API Keys (on Dashboard Load/Refresh):**
    *   Frontend -> Backend: `GET /auth/keys` with JWT.
    *   Backend -> Frontend: List of API Keys (prefixes only).
    *   Frontend: Renders the list.

7.  **Delete API Key:**
    *   User clicks "Delete" for a specific key.
    *   Frontend: Shows confirmation prompt.
    *   Frontend -> Backend: `DELETE /auth/keys/{key_id}` with JWT.
    *   Backend: Deactivates/deletes the key.
    *   Frontend: Removes key from the list upon success.

8.  **Revoke Delegation:**
    *   User clicks "Revoke Current Delegation".
    *   Frontend -> Backend: `GET /auth/delegation/active` with JWT (to get ID if needed).
    *   Frontend -> Backend: `DELETE /auth/delegation/{delegation_id}` with JWT.
    *   Backend: Deletes or marks delegation inactive.
    *   Frontend: Updates UI ("Delegation Status: Inactive", disables "Generate API Key" button).

## Flow Summary

This design ensures:
- **Clear Separation:** Web2 auth controls access to the Gateway UI/API key management; Web3 delegation controls the Gateway's permission to act on the blockchain.
- **Security:** User private keys are never exposed to the Gateway.
- **User Control:** Users explicitly grant and can revoke delegation.
- **Functionality:** API key generation is gated by successful delegation. 