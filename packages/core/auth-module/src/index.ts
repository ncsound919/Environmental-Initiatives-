/**
 * ECOS Authentication Module
 * Shared Auth0/Web3 authentication for all 13 projects
 */

import { z } from 'zod';
import jwt from 'jsonwebtoken';

// ============================================
// SCHEMAS
// ============================================

export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  auth0Id: z.string().optional(),
  web3Address: z.string().optional(),
  name: z.string().optional(),
  role: z.enum(['USER', 'ADMIN', 'OPERATOR', 'RESEARCHER']).default('USER'),
});

export const AuthTokenSchema = z.object({
  userId: z.string().uuid(),
  email: z.string().email(),
  role: z.string(),
  projectAccess: z.array(z.string()),
  iat: z.number(),
  exp: z.number(),
});

export type User = z.infer<typeof UserSchema>;
export type AuthToken = z.infer<typeof AuthTokenSchema>;

// ============================================
// AUTH SERVICE
// ============================================

export class AuthService {
  private jwtSecret: string;

  constructor(jwtSecret?: string) {
    const resolvedSecret = jwtSecret ?? process.env.JWT_SECRET;

    if (!resolvedSecret) {
      if (process.env.NODE_ENV === 'production') {
        throw new Error('JWT secret must be provided in production environment');
      }
      this.jwtSecret = 'dev-secret';
      return;
    }

    this.jwtSecret = resolvedSecret;
  }

  /**
   * Generate JWT token for authenticated user
   */
  generateToken(user: User, projectAccess: string[] = []): string {
    const payload: Omit<AuthToken, 'iat' | 'exp'> = {
      userId: user.id,
      email: user.email,
      role: user.role,
      projectAccess,
    };

    return jwt.sign(payload, this.jwtSecret, {
      expiresIn: '24h',
    });
  }

  /**
   * Verify and decode JWT token
   */
  verifyToken(token: string): AuthToken {
    try {
      const decoded = jwt.verify(token, this.jwtSecret);
      return AuthTokenSchema.parse(decoded);
    } catch (error) {
      throw new Error('Invalid or expired token');
    }
  }

  /**
   * Check if user has access to specific project
   */
  hasProjectAccess(token: AuthToken, projectCode: string): boolean {
    if (token.role === 'ADMIN') return true;
    return token.projectAccess.includes(projectCode);
  }

  /**
   * Middleware for protected routes
   */
  authenticateRequest(authHeader: string | undefined): AuthToken {
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new Error('Missing or invalid authorization header');
    }

    const token = authHeader.substring(7);
    return this.verifyToken(token);
  }
}

// ============================================
// ROLE-BASED ACCESS CONTROL
// ============================================

export const ProjectPermissions = {
  P01_FOAM_HOMES: ['USER', 'ADMIN', 'OPERATOR'],
  P02_SYMBIOSIS: ['USER', 'ADMIN', 'RESEARCHER'],
  P03_FARM: ['USER', 'ADMIN', 'OPERATOR'],
  P04_HEMP_LAB: ['ADMIN', 'RESEARCHER'],
  P05_GREENHOUSE: ['USER', 'ADMIN', 'RESEARCHER'],
  P06_REACTOR: ['ADMIN', 'RESEARCHER'],
  P07_BIOREACTOR: ['ADMIN', 'OPERATOR', 'RESEARCHER'],
  P08_BULB: ['USER', 'ADMIN', 'OPERATOR'],
  P09_AWG: ['USER', 'ADMIN', 'OPERATOR'],
  P10_GEOTHERMAL: ['USER', 'ADMIN', 'OPERATOR'],
  P11_RESERVED: ['ADMIN'],
  P12_SOLAR: ['USER', 'ADMIN', 'OPERATOR'],
  P13_HYDRO: ['USER', 'ADMIN', 'OPERATOR'],
} as const;

export function checkProjectPermission(
  userRole: string,
  projectCode: keyof typeof ProjectPermissions
): boolean {
  const allowedRoles = ProjectPermissions[projectCode];
  return allowedRoles.includes(userRole as any);
}

// ============================================
// EXPORTS
// ============================================

export const authService = new AuthService();

export default {
  AuthService,
  authService,
  UserSchema,
  AuthTokenSchema,
  ProjectPermissions,
  checkProjectPermission,
};
