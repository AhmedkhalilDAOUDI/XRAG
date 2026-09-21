import type { Metadata } from 'next';
import './globals.css';
export const metadata:Metadata={title:'N6 — Enterprise Knowledge',description:'Explore documents, trace relationships, and answer questions with cited evidence.',icons:{icon:'/favicon.svg'}};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>;}
