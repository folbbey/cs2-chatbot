from util.commands import command_registry

@command_registry.register('quest')
def quest_command(bot, is_team: bool, playername: str, chattext: str) -> None:
    """View or claim regular quests. Usage: @quest [claim]"""
    quest_module = bot.modules.get_module('quests')
    if not quest_module:
        bot.add_to_chat_queue(is_team, "Quest system not available.")
        return
    
    args = chattext.split()
    
    if args and args[0].lower() == 'claim':
        success, msg = quest_module.claim_all_regular_quests(playername)
        bot.add_to_chat_queue(is_team, msg)
        return
    
    # Show available quests with status
    all_quests = quest_module.get_regular_quests()
    claimable = quest_module.get_claimable_quests(playername)
    claimable_ids = {q['id'] for q in claimable}
    
    if not all_quests:
        bot.add_to_chat_queue(is_team, "No regular quests available.")
        return
    
    output = ["=== Regular Quests ==="]
    for quest in all_quests:
        status = "✓ Ready" if quest['id'] in claimable_ids else "✗ Missing items"
        req_text = ", ".join([f"{r['quantity']}x {r['name']}" for r in quest['requirements']])
        output.append(f"[{status}] {quest['title']}")
        output.append(f"  Requires: {req_text}")
        output.append(f"  Reward: ${quest['reward_money']:,}")
    
    output.append("")
    if claimable:
        output.append(f"Use @quest claim to claim {len(claimable)} ready quest(s)!")
    else:
        output.append("Keep fishing to complete quests!")
    
    bot.add_to_chat_queue(is_team, "\n".join(output))

@command_registry.register('daily')
def daily_command(bot, is_team: bool, playername: str, chattext: str) -> None:
    """View or claim your daily quest. Usage: @daily [claim]"""
    quest_module = bot.modules.get_module('quests')
    if not quest_module:
        bot.add_to_chat_queue(is_team, "Quest system not available.")
        return
    
    args = chattext.split()
    
    if args and args[0].lower() == 'claim':
        success, msg = quest_module.claim_daily_quest(playername)
        bot.add_to_chat_queue(is_team, msg)
        return
    
    # Show current daily quest
    quest = quest_module.get_daily_quest(playername)
    
    if not quest:
        bot.add_to_chat_queue(is_team, "No daily quest available.")
        return
    
    req_text = ", ".join([f"{r['quantity']}x {r['name']}" for r in quest['requirements']])
    
    output = [
        "=== Daily Quest ===",
        f"{quest['title']}",
        f"{quest['description']}",
        f"",
        f"Requirements: {req_text}",
        f"Reward: ${quest['reward_money']:,}",
        f"",
        "Use @daily claim to complete and claim your reward!"
    ]
    
    bot.add_to_chat_queue(is_team, "\n".join(output))
