from paper_utils import notify_discord, all_papers

paper = all_papers()[0]
print("Sent:", notify_discord(paper["filename"], paper))
