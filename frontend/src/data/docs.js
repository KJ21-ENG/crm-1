export const documentationData = [
  {
    title: "Getting Started",
    pages: [
      {
        id: "intro",
        title: "Introduction",
        content: [
          { type: "text", value: "<p>Welcome to the <strong>Eshin Broking CRM</strong>. This system is designed specifically for financial services professionals to manage client relationships, track portfolios, and ensure regulatory compliance.</p>" },
          { type: "note", value: "This CRM is tailored for Eshin Broking workflows. Standard Frappe CRM features may have been modified or renamed." },
          { type: "text", value: "<p>The interface is divided into key modules accessible via the sidebar. The Dashboard provides a high-level overview of your open tasks, new prospects, and portfolio performance.</p>" },
          { type: "image", alt: "CRM Dashboard Overview", caption: "The main dashboard showing key metrics and navigation.", src: "/assets/docs/dashboard-overview.png" }
        ]
      },
      {
        id: "navigation",
        title: "Navigation & Layout",
        content: [
          { type: "text", value: "<p>The sidebar is your main navigation tool. It can be collapsed to save screen space.</p>" },
          { type: "image", alt: "Sidebar Navigation", caption: "Sidebar expanded showing all modules.", src: "" }
        ]
      }
    ]
  },
  {
    title: "Prospect Management",
    pages: [
      {
        id: "prospects-overview",
        title: "Managing Prospects",
        content: [
          { type: "text", value: "<p><strong>Prospects</strong> (formerly Leads) represent potential clients. They are the entry point of your sales funnel.</p>" },
          { type: "image", alt: "Prospect List View", caption: "List of active prospects with status filters.", src: "/assets/docs/prospect-list.png" },
          { type: "text", value: "<h3>Creating a New Prospect</h3><p>Click the <strong>New Prospect</strong> button in the top right. Ensure you fill in the 'Source' and 'Investment Interest' fields correctly as these determine assignment logic.</p>" },
          { type: "image", alt: "New Prospect Form", caption: "The creation form with mandatory fields highlighted.", src: "/assets/docs/new-prospect-form.png" }
        ]
      },
      {
        id: "assignment",
        title: "Lead Assignment",
        content: [
          { type: "text", value: "<p>Prospects are assigned to Relationship Managers (RMs) based on load balancing or manual intervention.</p>" },
          { type: "note", value: "Assignments expire if not accepted within 24 hours." },
          { type: "image", alt: "Assignment Request Notification", caption: "How an assignment request appears to an RM.", src: "" }
        ]
      }
    ]
  },
  {
    title: "Compliance & KYC",
    pages: [
      {
        id: "compliance-record",
        title: "Compliance Records",
        content: [
          { type: "text", value: "<p>Before a Prospect can become a Client, a <strong>Compliance Record</strong> must be created and approved. This tracks KYC documents and risk profiling.</p>" },
          { type: "image", alt: "Compliance Record Tab", caption: "The Compliance tab within a Prospect page.", src: "/assets/docs/compliance-upload.png" },
          { type: "text", value: "<h3>Uploading Documents</h3><p>Use the 'Attachments' section to upload ID proofs and address verification. The system validates file types automatically.</p>" },
          { type: "image", alt: "Document Upload Section", caption: "Uploading KYC documents.", src: "/assets/docs/compliance-upload.png" }
        ]
      }
    ]
  },
  {
    title: "Client Accounts",
    pages: [
      {
        id: "accounts",
        title: "Client Portfolios",
        content: [
          { type: "text", value: "<p>Once a Prospect is converted, they become a <strong>Client Account</strong>. Here you manage their Portfolios and track AUM (Assets Under Management).</p>" },
          { type: "image", alt: "Client Account Overview", caption: "Client dashboard showing total portfolio value.", src: "/assets/docs/client-account.png" }
        ]
      }
    ]
  }
];
