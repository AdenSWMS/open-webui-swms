export type RoadmapStatus = 'done' | 'in-progress' | 'planned';

export type RoadmapItem = {
	title: string;
	date?: string;
	description?: string;
	status: RoadmapStatus;
};

export const roadmap: RoadmapItem[] = [
	{ title: 'Budget Guard', date: 'Q3 2026', status: 'done' },
	{ title: 'Überarbeiten des Projekt-Tabs', date: 'Q3 2026', status: 'done' },
	{ title: 'User Budget Einstellungen für Admins', date: 'Q3 2026', status: 'done' },
	{ title: 'User Budget Erweiterungsanfragen', date: 'Q3 2026', status: 'done' },
	{ title: 'OpenCode Sandbox', date: 'Q4 2026', status: 'in-progress' },
	{ title: 'Mehr Project-Features für Nutzer', date: 'Q4 2026', status: 'planned' }
];
