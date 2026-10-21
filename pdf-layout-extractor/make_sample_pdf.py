"""Create a 2-page SAMPLE PDF (live text) with bold/italic, wrapped paragraphs and a table."""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
st = getSampleStyleSheet()
doc = SimpleDocTemplate("sample/input_sample.pdf", pagesize=A4)
P = lambda t, s="BodyText": Paragraph(t, st[s])
story = [P("Quarterly Operations Note (Sample Document)", "Title"),
 P("This is a <b>synthetic sample</b> created to demonstrate layout-preserving extraction. It mixes <b>bold</b>, <i>italic</i> and <b><i>bold-italic</i></b> words inside normal wrapped paragraphs so the emphasis tags can be checked line by line."),
 Spacer(1, 8), P("1. Summary", "Heading2"),
 P("Orders grew <b>18%</b> quarter on quarter. Delivery times improved, although <i>returns</i> in the electronics category remain above target. The team recommends a <b>weekly</b> review until the rate falls below <i>3 per cent</i>."),
 Spacer(1, 8), P("2. Key figures", "Heading2"),
 Table([["Metric", "Q2", "Q3", "Change"], ["Orders", "12,400", "14,632", "+18.0%"], ["Avg. delivery (days)", "4.1", "3.6", "-0.5"], ["Return rate", "3.9%", "3.7%", "-0.2 pts"]],
       style=TableStyle([("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("GRID", (0, 0), (-1, -1), .5, colors.grey), ("ALIGN", (1, 0), (-1, -1), "RIGHT")]), hAlign="LEFT"),
 PageBreak(), P("3. Next steps", "Heading2"),
 P("• Pilot the new courier partner in <b>two cities</b>.<br/>• Publish the <i>returns playbook</i> for the support team.<br/>• Re-check all figures before the <b><i>final board pack</i></b>."),
 Spacer(1, 10), P("<i>Prepared as demo content; all numbers are invented.</i>")]
doc.build(story)
