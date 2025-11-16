import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
  try {
    const filePath = path.join(process.cwd(), 'backend', 'data', 'reminders', 'bill_reminders.json');
    const fileContents = fs.readFileSync(filePath, 'utf8');
    const reminders = JSON.parse(fileContents);
    
    return NextResponse.json(reminders);
  } catch (error) {
    console.error('Error reading reminders:', error);
    return NextResponse.json({ error: 'Failed to load reminders' }, { status: 500 });
  }
}
