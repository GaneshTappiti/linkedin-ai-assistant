import json
from datetime import datetime

colleges_data = [
    {"name": "Raghu Engineering College", "domain": "@raghuenggcollege.in", "users": 495, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Host Anchor / Beachhead"},
    {"name": "GITAM (Deemed to be University)", "domain": "@gitam.edu", "users": 12, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Deemed University / P0 Node"},
    {"name": "ANITS", "domain": "@anits.edu.in", "users": 10, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Private Engineering / P0 Node"},
    {"name": "mvgrce.edu.in", "domain": "@mvgrce.edu.in", "users": 5, "status": "Verified", "region": "Vizianagaram, Andhra Pradesh", "type": "Autonomous Engineering / P1 Node"},
    {"name": "VIT University, Vellore", "domain": "@vitstudent.ac.in", "users": 3, "status": "Verified", "region": "Vellore, Tamil Nadu", "type": "Premier National Private University"},
    {"name": "Gvpce", "domain": "@gvpce.ac.in", "users": 3, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Autonomous Engineering / P0 Node"},
    {"name": "Vignaniit", "domain": "@vignaniit.edu.in", "users": 3, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Autonomous Engineering / P0 Node"},
    {"name": "Ajay Kumar Garg Engineering College, Ghaziabad", "domain": "@akgec.ac.in", "users": 2, "status": "Verified", "region": "Ghaziabad, Uttar Pradesh", "type": "AKTU Engineering Node"},
    {"name": "Vellore Institute of Technology, Amravati", "domain": "@vitapstudent.ac.in", "users": 2, "status": "Verified", "region": "Amaravati, Andhra Pradesh", "type": "AP Capital Tech Corridor Node"},
    {"name": "Sagi Ramakrishnam Raju Engineering College", "domain": "@srkrec.ac.in", "users": 2, "status": "Verified", "region": "Bhimavaram, Andhra Pradesh", "type": "Autonomous Engineering / AP Coastal Corridor"},
    {"name": "Nsrit", "domain": "@nsrit.edu.in", "users": 2, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Autonomous Engineering / P1 Node"},
    {"name": "Fr Conceicao Rodrigues College Of Engineering Noedu", "domain": "@fr-conceicao-rodrigues-college-of-engineering.noedu", "users": 1, "status": "Unverified", "region": "Mumbai, Maharashtra", "type": "Tier-2 No-Edu Registration"},
    {"name": "Delhi Technical Campus", "domain": "@delhitechnicalcampus.ac.in", "users": 1, "status": "Verified", "region": "Greater Noida, Delhi-NCR", "type": "GGSIPU Affiliated College"},
    {"name": "Vignan S Institute Of Engineering For Women Noedu", "domain": "@vignan-s-institute-of-engineering-for-women.noedu", "users": 1, "status": "Unverified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Tier-2 No-Edu Registration"},
    {"name": "Somaiya Vidyavihar", "domain": "@somaiya.edu", "users": 1, "status": "Verified", "region": "Mumbai, Maharashtra", "type": "Private University Node"},
    {"name": "Shiv Nadar University, Greater Noida", "domain": "@snu.edu.in", "users": 1, "status": "Verified", "region": "Greater Noida, Uttar Pradesh", "type": "Premier Research University"},
    {"name": "Sreenidhi Institute Of Science And Technology Noedu", "domain": "@sreenidhi-institute-of-science-and-technology.noedu", "users": 1, "status": "Verified", "region": "Hyderabad, Telangana", "type": "Tier-2 No-Edu Registration (Verified)"},
    {"name": "NIT, Nagpur", "domain": "@students.vnit.ac.in", "users": 1, "status": "Verified", "region": "Nagpur, Maharashtra", "type": "Institute of National Importance (NIT)"},
    {"name": "THDC Institute Of Hydropower Engineering & Technology", "domain": "@thdcihet.ac.in", "users": 1, "status": "Verified", "region": "Tehri Garhwal, Uttarakhand", "type": "State Government Engineering College"},
    {"name": "INSTITUTE OF ENGINEERING & MANAGEMENT", "domain": "@iem.edu.in", "users": 1, "status": "Verified", "region": "Kolkata, West Bengal", "type": "Autonomous Engineering Node"},
    {"name": "Bitspilani Digital", "domain": "@bitspilani-digital.edu.in", "users": 1, "status": "Verified", "region": "Pilani / Pan-India", "type": "Institute of Eminence (BITS Pilani)"},
    {"name": "Devi Ahilya University of Indore", "domain": "@davv.ac.in", "users": 1, "status": "Verified", "region": "Indore, Madhya Pradesh", "type": "State University Node"},
    {"name": "Avanthi Institute Of Engineering And Technology Tagarapuvalasa Noedu", "domain": "@avanthi-institute-of-engineering-and-technology-tagarapuvalasa.noedu", "users": 1, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Autonomous Engineering / Tagarapuvalasa Cluster"},
    {"name": "Rns Institute Of Technology Noedu", "domain": "@rns-institute-of-technology.noedu", "users": 1, "status": "Verified", "region": "Bengaluru, Karnataka", "type": "Autonomous Engineering Node"},
    {"name": "SRM University", "domain": "@srmap.edu.in", "users": 1, "status": "Verified", "region": "Amaravati, Andhra Pradesh", "type": "AP Capital Tech Corridor Node"},
    {"name": "Kumaraguru College of Technology", "domain": "@kct.ac.in", "users": 1, "status": "Verified", "region": "Coimbatore, Tamil Nadu", "type": "Autonomous Engineering Node"},
    {"name": "Vignan's Institute of Engineering for Women (VIEW)", "domain": "@view.edu.in", "users": 1, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Autonomous Engineering / Women's Campus"},
    {"name": "National Institute of Fashion Technology", "domain": "@nift.ac.in", "users": 1, "status": "Verified", "region": "Pan-India", "type": "Statutory Institute of National Importance"},
    {"name": "N.M.A.M. Institute of Technology", "domain": "@nmamit.in", "users": 1, "status": "Verified", "region": "Nitte, Karnataka", "type": "Constituent College of Nitte University"},
    {"name": "Student Lnu Se", "domain": "@student.lnu.se", "users": 1, "status": "Verified", "region": "Vaxjo / Kalmar, Sweden", "type": "International University / Organic Outlier"},
    {"name": "SRM Institute of Science & Technology, Kattankalathur", "domain": "@srmist.edu.in", "users": 1, "status": "Verified", "region": "Chennai, Tamil Nadu", "type": "Deemed University / Main Campus"},
    {"name": "G.V.P COLLEGE OF ENGINEERING FOR WOMEN", "domain": "@gvpcew.ac.in", "users": 1, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Autonomous Engineering / Women's Campus"},
    {"name": "REVA University", "domain": "@reva.edu.in", "users": 1, "status": "Verified", "region": "Bengaluru, Karnataka", "type": "Private University Node"},
    {"name": "K.C. College of Engineering & Management Studies & Research", "domain": "@kccemsr.edu.in", "users": 1, "status": "Verified", "region": "Thane / Mumbai, Maharashtra", "type": "Mumbai University Affiliated College"},
    {"name": "B. S. Abdur Rahman Crescent Institute Of Science And Technology", "domain": "@crescent.education", "users": 1, "status": "Verified", "region": "Chennai, Tamil Nadu", "type": "Deemed University Node"},
    {"name": "Aditya College of Engineering & Tech", "domain": "@acet.ac.in", "users": 1, "status": "Verified", "region": "Surampalem / Kakinada, Andhra Pradesh", "type": "Autonomous Engineering / Godavari Corridor"},
    {"name": "RAJIV GANDHI UNIVERSITY OF KNOWLEDGE TECHNOLOGIES, ONGOLE", "domain": "@rguktong.ac.in", "users": 1, "status": "Verified", "region": "Ongole, Andhra Pradesh", "type": "State Autonomous University (IIIT AP)"},
    {"name": "National Institute of Technology Durgapur", "domain": "@nitdgp.ac.in", "users": 1, "status": "Verified", "region": "Durgapur, West Bengal", "type": "Institute of National Importance (NIT)"},
    {"name": "SASTRA University", "domain": "@sastra.ac.in", "users": 1, "status": "Verified", "region": "Thanjavur, Tamil Nadu", "type": "Category 1 Deemed University"},
    {"name": "Andhrauniversity", "domain": "@andhrauniversity.edu.in", "users": 1, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "State Flagship University / AUCE Node"},
    {"name": "Aietta", "domain": "@aietta.ac.in", "users": 1, "status": "Verified", "region": "Visakhapatnam, Andhra Pradesh", "type": "Autonomous Engineering Node"},
    {"name": "Koneru Lakshmaiah Education Foundation", "domain": "@kluniversity.in", "users": 1, "status": "Verified", "region": "Vijayawada / Guntur, Andhra Pradesh", "type": "Deemed University / AP Tech Corridor"},
    {"name": "Lendi", "domain": "@lendi.edu.in", "users": 1, "status": "Verified", "region": "Jonnada / Vizianagaram, Andhra Pradesh", "type": "Autonomous Engineering Node"},
    {"name": "Pvpsit", "domain": "@pvpsit.ac.in", "users": 1, "status": "Verified", "region": "Vijayawada, Andhra Pradesh", "type": "Autonomous Engineering Node"},
    {"name": "Indian Institute of Information Technology, Design and Manufacturing, Kancheepuram", "domain": "@iiitdm.ac.in", "users": 1, "status": "Verified", "region": "Chennai, Tamil Nadu", "type": "Institute of National Importance (IIIT)"},
    {"name": "Uem", "domain": "@uem.edu.in", "users": 1, "status": "Verified", "region": "Kolkata / Jaipur", "type": "Private University Node"},
    {"name": "maricopa.edu", "domain": "@maricopa.edu", "users": 1, "status": "Verified", "region": "Arizona, United States", "type": "International Community College / Outlier"}
]

total_students = sum(c['users'] for c in colleges_data)
total_colleges = len(colleges_data)
verified_colleges = len([c for c in colleges_data if c['status'] == 'Verified'])
unverified_colleges = len([c for c in colleges_data if c['status'] == 'Unverified'])

payload = {
    "extracted_at": "2026-11-14T08:15:00+05:30",
    "source": "clstr.in Admin Dashboard",
    "metrics_summary": {
        "total_students": total_students,
        "total_colleges": total_colleges,
        "verified_colleges": verified_colleges,
        "unverified_colleges": unverified_colleges,
        "flagged_colleges": 0
    },
    "cluster_breakdown": {
        "host_beachhead": {
            "college": "Raghu Engineering College",
            "users": 495,
            "share_pct": round(495 / total_students * 100, 2)
        },
        "vizag_ap_corridor": {
            "colleges_count": 20,
            "description": "Visakhapatnam, Vizianagaram, Godavari, Amaravati & Vijayawada corridor nodes (GITAM, ANITS, MVGR, GVPCE, VIIT, NSRIT, SRKR, VIEW, GVPW, AU, AIETTA, Lendi, KL University, PVPSIT, Aditya, RGUKT Ongole, VIT-AP, SRM-AP)",
            "users": 495 + 12 + 10 + 5 + 3 + 3 + 2 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 1  # 546 users!
        },
        "national_premier_and_outstation": {
            "description": "NITs, IIIT, BITS Pilani, VIT Vellore, SNU, IEM, AKGEC, REVA, etc.",
            "users": total_students - 546 - 2  # minus international
        },
        "international": {
            "description": "Linnaeus University (Sweden), Maricopa Community Colleges (USA)",
            "users": 2
        }
    },
    "colleges": colleges_data
}

with open('data-tracking/clstr_admin_dashboard_snapshot_2026-11-14.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2)

print(f"Snapshot written successfully: {total_students} students across {total_colleges} colleges ({verified_colleges} verified, {unverified_colleges} unverified).")

