from telethon import TelegramClient, events
from telethon.tl.functions.channels import (
    CreateChannelRequest,
    InviteToChannelRequest,
    EditAdminRequest,
    EditPhotoRequest,
    DeleteChannelRequest
)
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import (
    ChatAdminRights,
    InputChatUploadedPhoto,
    MessageActionChatAddUser,
    MessageActionChatJoinedByLink,
    MessageActionChatEditPhoto,
    MessageActionChatEditTitle,
    MessageActionChatDeletePhoto
)
import asyncio

# ── Config ────────────────────────────────────────────────────────────────
api_id = 34365075
api_hash = "23c4c0cd9fef652b967d9f2b66cbf560"

CREATEGROUP_ADMIN = "Shuify"

PFP1 = "Pfp1.jpg"

# ── YAHAN BOT KA USERNAME DAALO (e.g., "@SecurebleBot") ──────────────
BOT_USERNAME = "@Secureblebot"
BOT_TITLE = "Secureble Bot"

DEAL_START = 266

admin_rights = ChatAdminRights(
    change_info=True,
    post_messages=True,
    edit_messages=True,
    delete_messages=True,
    ban_users=True,
    invite_users=True,
    pin_messages=True,
    add_admins=False,
    anonymous=False,
    manage_call=True
)

client = TelegramClient("session", api_id, api_hash)
deal_counter = DEAL_START

# ── Admin list (jinke alawa sab ignore) ───────────────────────────────────
# Sirf ye log admin commands use kar sakte hain
ADMIN_USERNAMES = {"shuify", "dochains"}  # case-insensitive, lowercase rakho


def is_admin(sender):
    """Check if sender is in admin list by username."""
    try:
        username = sender.username
        if username and username.lower() in ADMIN_USERNAMES:
            return True
    except:
        pass
    return False


async def create_deal_group(event, pfp, admin_id):
    global deal_counter
    deal_num = deal_counter
    deal_counter += 1
    title = f"Deal #{deal_num} • @Secureble"

    try:
        # Create group
        result = await client(CreateChannelRequest(
            title=title,
            about="Always confirm that you are dealing with me and not with an impersonator!",
            megagroup=True
        ))

        chat = result.chats[0]
        admin = await client.get_input_entity(admin_id)
        creator = await client.get_me()

        # Invite admin
        await client(InviteToChannelRequest(chat, [admin]))

        # Admin tag
        await client(EditAdminRequest(
            channel=chat,
            user_id=admin,
            admin_rights=admin_rights,
            rank="Middleman"
        ))

        # Creator tag
        await client(EditAdminRequest(
            channel=chat,
            user_id=creator,
            admin_rights=admin_rights,
            rank="Secureble Group"
        ))

        # Upload PFP
        file = await client.upload_file(pfp)
        await client(EditPhotoRequest(
            channel=chat,
            photo=InputChatUploadedPhoto(file)
        ))

        # ── Add Bot with title "Secureble Bot" ────────────────────────
        bot_entity = await client.get_input_entity(BOT_USERNAME)
        await client(InviteToChannelRequest(chat, [bot_entity]))
        await client(EditAdminRequest(
            channel=chat,
            user_id=bot_entity,
            admin_rights=admin_rights,
            rank=BOT_TITLE
        ))

        # Invite link
        invite = await client(ExportChatInviteRequest(chat))
        await event.reply(f"✅ Group Created – Deal {deal_num}\n\n{invite.link}")

        return chat.id, deal_num

    except Exception as e:
        await event.reply(f"❌ Error:\n{e}")
        return None, None


# ── /ziox – Sirf admin ko reply ──────────────────────────────────────────
@client.on(events.NewMessage(pattern="/shuify"))
async def ziox_group(event):
    sender = await event.get_sender()
    if not is_admin(sender):
        return  # 👈 ignore karo, koi reply nahi
    await create_deal_group(event, PFP1, CREATEGROUP_ADMIN)


# ── /close – Sirf admin ko reply ─────────────────────────────────────────
@client.on(events.NewMessage(pattern="/close"))
async def close_deal(event):
    sender = await event.get_sender()
    if not is_admin(sender):
        return  # 👈 ignore karo, koi reply nahi
    msg = (
        "🤝 This deal is now closed with status: Successful.\n\n"
        "The group will be deleted automatically in 30 minutes."
    )
    sent = await event.reply(msg)
    await asyncio.sleep(1800)
    try:
        await client(DeleteChannelRequest(event.chat_id))
    except Exception:
        pass


# ── Auto-delete service messages ─────────────────────────────────────────
@client.on(events.NewMessage)
async def delete_service_messages(event):
    try:
        if isinstance(event.message.action, (
            MessageActionChatAddUser,
            MessageActionChatJoinedByLink,
            MessageActionChatEditPhoto,
            MessageActionChatEditTitle,
            MessageActionChatDeletePhoto
        )):
            await event.delete()
    except:
        pass


print("🔥 Auto MM Group Creator Running... (Deals start from 261)")

client.start()
client.run_until_disconnected()