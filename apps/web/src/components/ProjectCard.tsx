import type { Project } from '@/lib/data';
import { withOpacity } from '@/lib/utils';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <div className="project-card">
      <div className="project-header">
        <div 
          className="project-icon" 
          style={{ backgroundColor: withOpacity(project.color, 12) }}
        >
          {project.icon}
        </div>
        <span className={`project-badge ${project.readiness > 0 ? 'badge-active' : 'badge-reserved'}`}>
          {project.readiness > 0 ? `${project.readiness}% Ready` : 'Reserved'}
        </span>
      </div>
      <h3 className="project-name">{project.name}</h3>
      <p className="project-type">{project.type}</p>
      <p className="project-description">{project.description}</p>
      <div className="project-features">
        {project.features.slice(0, 3).map((feature, index) => (
          <span key={index} className="feature-tag">{feature}</span>
        ))}
      </div>
    </div>
  );
}
