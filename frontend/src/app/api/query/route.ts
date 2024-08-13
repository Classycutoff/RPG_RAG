// pages/api/query.ts

// import type { NextApiRequest, NextApiResponse } from 'next';
import { NextResponse } from 'next/server';
import { Result } from '../../../types';

// function isEmptyArray(value: any): value is Array<any> {
//   return Array.isArray(value) && value.length === 0;
// }

function removeDuplicates(results: Result[]) {
  const seen = new Set<string>();
  return results.filter(result => {
    const key = `${result.metadata.source}-${result.metadata.page}`;
    if (seen.has(key)) {
      return false;
    } else {
      seen.add(key);
      return true;
    }
  })
}

export async function POST(request: Request) {
  const body = await request.json();

  try {
    const response = await fetch('http://backend:5001/api/query', {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error('Error from backend' );
    }

    let data = await response.json();
    let filtered_results = removeDuplicates(data);
    // if (isEmptyArray(data)) {
    //   data = [{
    //     text: 'Empty array. Please add some pdf\'s',
    //     metada: {
    //       source: 'null',
    //       page: 'null'
    //     },
    //     image: 'null',
    //     distance: 0
    //   }];
    // }
    // console.log('POST DATA', data)
    return NextResponse.json({message: "Data received succesfully", filtered_results})
  } catch (error) {
    console.error('Error forwarding request to backend:', error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500});
  }
}