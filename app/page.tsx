import Workspace from '@/components/workspace';
import {requireChatGPTUser} from './chatgpt-auth';
import {runtime} from '@/lib/runtime';
export const dynamic='force-dynamic';
// In single-owner mode proxy.ts has already checked the password.
export default async function Home(){if(!runtime().APP_PASSWORD)await requireChatGPTUser('/');return <Workspace/>;}
