export type RoadmapStatus = 'done' | 'in-progress' | 'planned';

export type RoadmapItem = {
	title: string;
	date?: string;
	description?: string;
	status: RoadmapStatus;
};

export const roadmap: RoadmapItem[] = [
	{ title: 'User Budget Einstellunge für Admins', date: 'Q4 2026', status: 'in-progress' },
	{ title: 'OpenCode Sandbox', date: 'Q4 2026', status: 'in-progress' },
	{ title: 'Mehr Project-Features für Nutzer', date: 'Q4 2026', status: 'planned' }
];
