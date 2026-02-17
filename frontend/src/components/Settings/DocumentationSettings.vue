<template>
  <div class="h-full overflow-y-auto p-6">
    <div class="mx-auto max-w-5xl space-y-6">
      <div>
        <h2 class="text-2xl font-semibold text-ink-gray-9">{{ __('User Documentation') }}</h2>
        <p class="mt-2 text-sm text-ink-gray-6">
          {{ __('Operator-focused guide for all important CRM modules. Follow each workflow step and refer to inline screenshots.') }}
        </p>
      </div>

      <div class="rounded-lg border bg-surface-gray-1 p-4">
        <div class="mb-3 text-sm font-medium text-ink-gray-7">{{ __('Quick Navigation') }}</div>
        <div class="flex flex-wrap gap-2">
          <Button
            v-for="mod in modules"
            :key="mod.key"
            size="sm"
            :variant="activeModule === mod.key ? 'solid' : 'subtle'"
            @click="activeModule = mod.key"
            :label="__(mod.title)"
          />
        </div>
      </div>

      <div v-if="currentModule" class="space-y-6">
        <div class="rounded-lg border bg-white p-5">
          <h3 class="text-xl font-semibold text-ink-gray-9">{{ __(currentModule.title) }}</h3>
          <p class="mt-2 text-sm text-ink-gray-7">{{ __(currentModule.overview) }}</p>
        </div>

        <div
          v-for="(section, sidx) in currentModule.sections"
          :key="`${currentModule.key}-section-${sidx}`"
          class="rounded-lg border bg-white p-5"
        >
          <h4 class="text-lg font-semibold text-ink-gray-8">{{ __(section.title) }}</h4>
          <div class="mt-4 space-y-6">
            <div
              v-for="(point, pidx) in section.points"
              :key="`${currentModule.key}-section-${sidx}-point-${pidx}`"
              class="space-y-3"
            >
              <div class="text-sm leading-6 text-ink-gray-8">
                <span class="font-medium">{{ pidx + 1 }}.</span>
                {{ __(point.text) }}
              </div>

              <div v-if="point.image" class="overflow-hidden rounded-md border bg-surface-gray-1">
                <img :src="point.image" :alt="point.imageAlt || point.text" class="w-full" />
                <div v-if="point.caption" class="border-t px-3 py-2 text-xs text-ink-gray-6">
                  {{ __(point.caption) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const modules = [
  {
    key: 'dashboard',
    title: 'Dashboard',
    overview: 'Use Dashboard for daily performance tracking, trend checks, and quick operational actions.',
    sections: [
      {
        title: 'Daily Monitoring',
        points: [
          { text: 'Open Dashboard from sidebar to review today\'s snapshot cards for leads, tickets, tasks, and call volume.', image: '/docs/screenshots/dashboard/01-overview.png', caption: 'Overview cards highlighted for quick daily check.' },
          { text: 'Use the date/view selector to switch between Daily, Weekly, and Custom ranges before taking decisions.', image: '/docs/screenshots/dashboard/02-date-range.png', caption: 'Date range controls and filter area.' },
          { text: 'Review team/user performance widgets to identify pending workload and handoff needs.', image: '/docs/screenshots/dashboard/03-performance.png', caption: 'Performance area used for supervision.' },
        ],
      },
    ],
  },
  {
    key: 'leads',
    title: 'Leads',
    overview: 'Leads module handles inquiry intake, qualification, follow-up, and account lifecycle transitions.',
    sections: [
      {
        title: 'Lead List Workflow',
        points: [
          { text: 'Create a new Lead using the Create button from Leads list view.', image: '/docs/screenshots/leads/01-list-create.png', caption: 'Create button and list controls.' },
          { text: 'Apply quick filters (status, owner, assigned user) to work only on your operational queue.', image: '/docs/screenshots/leads/02-list-filters.png', caption: 'Filter bar and active filtered result.' },
          { text: 'Use row actions to add Note, Task, or place Call without opening full detail page.', image: '/docs/screenshots/leads/03-list-actions.png', caption: 'Inline row action menu for fast operations.' },
        ],
      },
      {
        title: 'Lead Detail Tabs',
        points: [
          { text: 'In Activity tab, track complete lead timeline including status changes, assignments, and comments.', image: '/docs/screenshots/leads/04-detail-activity.png', caption: 'Activity timeline markers and latest events.' },
          { text: 'Use Calls tab to review linked customer calls and verify call outcomes before status updates.', image: '/docs/screenshots/leads/05-detail-calls.png', caption: 'Call history panel inside lead detail.' },
          { text: 'Use Tasks tab for follow-up commitments and ensure due items are completed on time.', image: '/docs/screenshots/leads/06-detail-tasks.png', caption: 'Lead-linked task list and due statuses.' },
          { text: 'Before moving to statuses like Account Opened / Sent to HO / Rejected Follow-up, complete mandatory fields prompted by modal.', image: '/docs/screenshots/leads/07-status-mandatory.png', caption: 'Status update modal with required fields highlighted.' },
        ],
      },
    ],
  },
  {
    key: 'tickets',
    title: 'Tickets',
    overview: 'Tickets module is used for issue intake, subject tagging, assignment, SLA handling, and closure.',
    sections: [
      {
        title: 'Ticket Handling',
        points: [
          { text: 'Create ticket from list view and capture customer details plus ticket subject(s) accurately.', image: '/docs/screenshots/tickets/01-list-create.png', caption: 'Ticket create flow entry point.' },
          { text: 'Use status and priority fields to classify urgency and expected response sequence.', image: '/docs/screenshots/tickets/02-priority-status.png', caption: 'Priority and status fields to drive workflow.' },
          { text: 'Track SLA section in ticket detail to avoid missed response or resolution commitments.', image: '/docs/screenshots/tickets/03-sla.png', caption: 'SLA indicator section highlighted.' },
        ],
      },
    ],
  },
  {
    key: 'customers',
    title: 'Customers',
    overview: 'Customers module maintains centralized customer identity and contact data used across leads and tickets.',
    sections: [
      {
        title: 'Customer Records',
        points: [
          { text: 'Search customer by mobile or name before creating duplicate records.', image: '/docs/screenshots/customers/01-search.png', caption: 'Customer search panel for dedupe.' },
          { text: 'Update profile details carefully because customer data syncs into linked lead/ticket experiences.', image: '/docs/screenshots/customers/02-profile-edit.png', caption: 'Customer profile editable fields.' },
          { text: 'Use interactions overview to understand all linked leads, tickets, and calls before next action.', image: '/docs/screenshots/customers/03-interactions.png', caption: 'Customer interactions section.' },
        ],
      },
    ],
  },
  {
    key: 'tasks',
    title: 'Tasks',
    overview: 'Tasks module ensures follow-up execution with assignment, due date discipline, and reminders.',
    sections: [
      {
        title: 'Task Execution',
        points: [
          { text: 'Create tasks with clear title, owner, due date, and priority so reminders are meaningful.', image: '/docs/screenshots/tasks/01-create.png', caption: 'Task create modal required fields.' },
          { text: 'Use task status transitions (Todo → In Progress → Completed) as the source of truth for work tracking.', image: '/docs/screenshots/tasks/02-status-flow.png', caption: 'Task status controls in list/detail.' },
          { text: 'Review Task Reminders panel from sidebar to avoid missed due items.', image: '/docs/screenshots/tasks/03-reminders.png', caption: 'Task notification panel and unread indicators.' },
        ],
      },
    ],
  },
  {
    key: 'calllogs',
    title: 'Call Logs',
    overview: 'Call Logs captures customer communication history and links it to operational entities for full traceability.',
    sections: [
      {
        title: 'Call Review and Filtering',
        points: [
          { text: 'Use Call Logs list for method/type/status-based monitoring of communication quality.', image: '/docs/screenshots/calllogs/01-list-overview.png', caption: 'Call logs list with key columns highlighted.' },
          { text: 'Apply date and owner filters to audit calls for a user or specific operational period.', image: '/docs/screenshots/calllogs/02-filters.png', caption: 'Filtering controls for audit views.' },
          { text: 'Open call row detail to verify linked lead/ticket context before callbacks or escalations.', image: '/docs/screenshots/calllogs/03-detail-links.png', caption: 'Linked context area in call detail.' },
        ],
      },
    ],
  },
  {
    key: 'notes',
    title: 'Notes',
    overview: 'Notes module is used for non-chat operational context, call outcomes, and handoff-quality updates.',
    sections: [
      {
        title: 'Operational Notes',
        points: [
          { text: 'Create concise notes with title and actionable content for future follow-up.', image: '/docs/screenshots/notes/01-create.png', caption: 'Note creation panel.' },
          { text: 'Attach notes to relevant Lead/Ticket so future operators can see context in one place.', image: '/docs/screenshots/notes/02-linked.png', caption: 'Reference link fields for notes.' },
        ],
      },
    ],
  },
  {
    key: 'supportpages',
    title: 'Support Pages',
    overview: 'Support Pages helps operators send standard guidance content quickly during issue resolution.',
    sections: [
      {
        title: 'Support Guidance Sharing',
        points: [
          { text: 'Create and categorize support pages with clear and reusable customer-facing content.', image: '/docs/screenshots/support-pages/01-create.png', caption: 'Support page form and content editor.' },
          { text: 'From ticket/lead context, send selected support pages to customer with optional custom message.', image: '/docs/screenshots/support-pages/02-send.png', caption: 'Support page sharing flow.' },
        ],
      },
    ],
  },
]

const activeModule = ref(modules[0].key)
const currentModule = computed(() => modules.find((m) => m.key === activeModule.value))
</script>
