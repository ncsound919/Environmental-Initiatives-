/**
 * Auth0 Integration Module for ECOS
 * Replaces JWT stub with real Auth0 tenant + RBAC
 */
import { expressjwt as jwt } from 'express-jwt';
import jwksRsa from 'jwks-rsa';
import { Request, Response, NextFunction } from 'express';

export type EcosRole = 'admin' | 'operator' | 'viewer' | 'device';

export interface EcosJwtPayload {
  sub: string;       // Auth0 user ID
  email?: string;
  name?: string;
  'https://ecos.app/roles': EcosRole[];
  'https://ecos.app/projects': number[];  // allowed project IDs
  iat: number;
  exp: number;
}

/** Auth0 config - set via environment variables */
const AUTH0_DOMAIN = process.env.AUTH0_DOMAIN ?? '';
const AUTH0_AUDIENCE = process.env.AUTH0_AUDIENCE ?? 'https://api.ecos.app';

/**
 * Middleware: Verify Auth0 JWT (RS256) on every protected route.
 * Validates signature against Auth0 JWKS endpoint.
 */
export const verifyAuth0Token = jwt({
  secret: jwksRsa.expressJwtSecret({
    cache: true,
    rateLimit: true,
    jwksRequestsPerMinute: 5,
    jwksUri: `https://${AUTH0_DOMAIN}/.well-known/jwks.json`,
  }),
  audience: AUTH0_AUDIENCE,
  issuer: `https://${AUTH0_DOMAIN}/`,
  algorithms: ['RS256'],
});

/**
 * RBAC middleware factory.
 * Usage: router.get('/admin-route', verifyAuth0Token, requireRole('admin'), handler)
 */
export function requireRole(...roles: EcosRole[]) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const user = (req as Request & { auth?: EcosJwtPayload }).auth;
    if (!user) {
      res.status(401).json({ error: 'Unauthorized: no token' });
      return;
    }
    const userRoles: EcosRole[] = user['https://ecos.app/roles'] ?? [];
    const hasRole = roles.some((r) => userRoles.includes(r));
    if (!hasRole) {
      res.status(403).json({
        error: 'Forbidden',
        required: roles,
        current: userRoles,
      });
      return;
    }
    next();
  };
}

/**
 * Project-level access guard.
 * Ensures the requesting user has access to the given project ID.
 */
export function requireProjectAccess(projectId: number) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const user = (req as Request & { auth?: EcosJwtPayload }).auth;
    if (!user) {
      res.status(401).json({ error: 'Unauthorized' });
      return;
    }
    const allowedProjects = user['https://ecos.app/projects'] ?? [];
    // Admins bypass project-level checks
    const isAdmin = (user['https://ecos.app/roles'] ?? []).includes('admin');
    if (!isAdmin && !allowedProjects.includes(projectId)) {
      res.status(403).json({
        error: `Access denied for project ${projectId}`,
      });
      return;
    }
    next();
  };
}

/**
 * Extract typed user from an authenticated request.
 */
export function getUser(req: Request): EcosJwtPayload | null {
  return ((req as Request & { auth?: EcosJwtPayload }).auth) ?? null;
}

/**
 * Auth0 Management API helper - get a Machine-to-Machine token
 * for backend operations (user management, role assignment).
 */
export async function getManagementApiToken(): Promise<string> {
  const clientId = process.env.AUTH0_M2M_CLIENT_ID;
  const clientSecret = process.env.AUTH0_M2M_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    throw new Error('AUTH0_M2M_CLIENT_ID and AUTH0_M2M_CLIENT_SECRET must be set');
  }
  const resp = await fetch(`https://${AUTH0_DOMAIN}/oauth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'client_credentials',
      client_id: clientId,
      client_secret: clientSecret,
      audience: `https://${AUTH0_DOMAIN}/api/v2/`,
    }),
  });
  if (!resp.ok) {
    throw new Error(`Auth0 M2M token request failed: ${resp.status}`);
  }
  const data = (await resp.json()) as { access_token: string };
  return data.access_token;
}

/**
 * Assign an ECOS role to an Auth0 user via the Management API.
 * Requires AUTH0_ADMIN_ROLE_ID_<ROLE> env vars set with Auth0 role UUIDs.
 */
export async function assignRoleToUser(
  userId: string,
  role: EcosRole,
): Promise<void> {
  const roleIdEnvKey = `AUTH0_ROLE_ID_${role.toUpperCase()}`;
  const roleId = process.env[roleIdEnvKey];
  if (!roleId) {
    throw new Error(`${roleIdEnvKey} environment variable not set`);
  }
  const token = await getManagementApiToken();
  const resp = await fetch(
    `https://${AUTH0_DOMAIN}/api/v2/users/${encodeURIComponent(userId)}/roles`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ roles: [roleId] }),
    },
  );
  if (!resp.ok) {
    throw new Error(`Failed to assign role: ${resp.status} ${await resp.text()}`);
  }
}

export default {
  verifyAuth0Token,
  requireRole,
  requireProjectAccess,
  getUser,
  getManagementApiToken,
  assignRoleToUser,
};
