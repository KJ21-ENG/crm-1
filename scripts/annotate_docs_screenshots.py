from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE = Path('/home/jainam/.openclaw/workspace/crm-1/frontend/public/docs/screenshots')

ANNOTATIONS = {
    'dashboard/01-overview.png': [((260,140,1180,420), 'Overview KPI cards')],
    'dashboard/02-date-range.png': [((240,80,900,150), 'Date range / filters')],
    'dashboard/03-performance.png': [((240,430,1220,820), 'Performance and trend widgets')],

    'leads/01-list-create.png': [((1100,80,1260,150), 'Create lead button')],
    'leads/02-list-filters.png': [((240,180,1200,260), 'Quick filters and controls')],
    'leads/03-list-actions.png': [((1120,330,1270,780), 'Row-level quick actions')],
    'leads/04-detail-activity.png': [((240,170,960,260), 'Lead tabs (Activity etc.)')],
    'leads/05-detail-calls.png': [((260,190,970,290), 'Calls tab area')],
    'leads/06-detail-tasks.png': [((260,190,970,290), 'Tasks tab area')],
    'leads/07-status-mandatory.png': [((990,80,1260,160), 'Status change dropdown / required flow')],

    'tickets/01-list-create.png': [((1110,80,1270,150), 'Create ticket button')],
    'tickets/02-priority-status.png': [((260,290,940,760), 'Priority and status columns')],
    'tickets/03-sla.png': [((980,240,1450,820), 'SLA and right-side details')],

    'customers/01-search.png': [((240,170,860,250), 'Customer search and filters')],
    'customers/02-profile-edit.png': [((1000,220,1460,840), 'Customer profile panel')],
    'customers/03-interactions.png': [((240,300,960,850), 'Customer interactions context')],

    'tasks/01-create.png': [((1110,80,1270,150), 'Create task button')],
    'tasks/02-status-flow.png': [((250,300,980,810), 'Task statuses and progression')],
    'tasks/03-reminders.png': [((20,160,220,250), 'Task reminders entry in sidebar')],

    'calllogs/01-list-overview.png': [((240,260,1240,860), 'Call log list with core columns')],
    'calllogs/02-filters.png': [((240,170,1180,250), 'Call log filters')],
    'calllogs/03-detail-links.png': [((970,250,1460,860), 'Linked lead/ticket context')],

    'notes/01-create.png': [((1110,80,1270,150), 'Create note button')],
    'notes/02-linked.png': [((260,300,980,860), 'Linked note reference context')],

    'support-pages/01-create.png': [((1110,80,1270,150), 'Create support page')],
    'support-pages/02-send.png': [((240,300,980,860), 'Support page sharing workflow')],
}


def draw_annot(path: Path, boxes):
    im = Image.open(path).convert('RGBA')
    overlay = Image.new('RGBA', im.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    for i, (box, label) in enumerate(boxes, start=1):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle(box, radius=10, outline=(220, 38, 38, 255), width=5, fill=(220, 38, 38, 40))
        # badge
        bx, by = x1 + 8, max(8, y1 - 34)
        draw.rounded_rectangle((bx, by, bx + 36, by + 30), radius=8, fill=(220, 38, 38, 255))
        draw.text((bx + 11, by + 4), str(i), fill=(255, 255, 255, 255), font=font)

        # label box
        tw = draw.textlength(label, font=small)
        lx1, ly1 = bx + 44, by
        lx2, ly2 = lx1 + tw + 20, by + 30
        draw.rounded_rectangle((lx1, ly1, lx2, ly2), radius=8, fill=(17, 24, 39, 220))
        draw.text((lx1 + 10, ly1 + 5), label, fill=(255, 255, 255, 255), font=small)

    out = Image.alpha_composite(im, overlay).convert('RGB')
    out.save(path, quality=95)


for rel, boxes in ANNOTATIONS.items():
    p = BASE / rel
    if p.exists():
        draw_annot(p, boxes)
        print('annotated', p)
    else:
        print('missing', p)
